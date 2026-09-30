/* CDD Assistant front end. No build step, no dependencies. All model and
   source text is inserted with textContent, never innerHTML. */
(() => {
  "use strict";

  const TIER_LABEL = {
    simplified: "Simplified CDD",
    standard: "Standard CDD",
    enhanced: "Enhanced CDD",
    insufficient_information: "Cannot determine",
  };
  const CONF_LEVEL = { low: 1, medium: 2, high: 3 };
  const MODE_COPY = {
    determine: {
      label: "Customer scenario",
      placeholder: "Describe the customer: legal form, who owns or controls it, PEP status, countries involved, the service, and your risk rating.",
      button: "Determine tier",
      emptyTitle: "No determination yet",
      emptyText: "Describe a customer scenario and the assistant will say which CDD tier applies, why, and which clause each point relies on.",
    },
    explain: {
      label: "Your question",
      placeholder: "Ask about a CDD obligation in plain words, e.g. “What do we need to collect for a sole trader?”",
      button: "Explain",
      emptyTitle: "Ask about an obligation",
      emptyText: "Get a plain-language explanation of an AML/CTF customer due diligence obligation, with each point cited to its source.",
    },
  };

  const $ = (id) => document.getElementById(id);
  let mode = "determine";
  let examples = { determine: [], explain: [] };
  let busy = false;

  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v === undefined || v === null || v === false) continue;
      if (k === "class") node.className = v;
      else if (k === "text") node.textContent = v;
      else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v === true ? "" : v);
    }
    for (const c of children.flat()) {
      if (c === null || c === undefined || c === false) continue;
      node.append(c instanceof Node ? c : document.createTextNode(String(c)));
    }
    return node;
  }

  async function api(path, body) {
    const opts = body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {};
    const res = await fetch(path, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail ? (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail)) : res.statusText);
    return data;
  }

  // ------------------------------------------------------------------ health
  async function loadHealth() {
    try {
      const h = await api("/api/health");
      if (!h.ok) throw new Error(h.error || "not ready");
      $("status-dot").className = "dot ok";
      $("status-text").textContent = `Knowledge base ${h.snapshot || "unversioned"} · ${h.chunks} passages · ${h.generator.replace("ollama:", "")}`;
      $("snapshot-note").textContent = h.snapshot ? ` Knowledge base snapshot: ${h.snapshot}.` : "";
      $("stub-banner").hidden = !h.offline_stub;
      const ql = h.query_log || {};
      const logged = !ql.enabled ? "Questions are not logged."
        : ql.store_text === "none" ? "Only outcomes are logged, not the question."
        : ql.store_text === "full" ? "Questions are logged as typed."
        : "Questions are logged with identifiers masked";
      const kept = ql.enabled && ql.retention_days ? ` and deleted after ${ql.retention_days} days.` : ql.enabled && ql.store_text !== "none" ? "." : "";
      $("privacy-note").textContent = `Describe the customer; don't type names, addresses or ID numbers. ${logged}${kept}`;
    } catch (err) {
      $("status-dot").className = "dot bad";
      $("status-text").textContent = `Not ready: ${err.message}`;
    }
  }

  // ------------------------------------------------------------------ tabs + examples
  function setMode(next) {
    mode = next;
    document.querySelectorAll(".tab").forEach((t) => {
      const on = t.dataset.tab === next;
      t.classList.toggle("active", on);
      t.setAttribute("aria-selected", on ? "true" : "false");
    });
    const ask = next !== "gaps";
    $("ask-view").hidden = !ask;
    $("gaps-view").hidden = ask;
    if (!ask) { loadGaps(); return; }
    const copy = MODE_COPY[next];
    $("query-label").textContent = copy.label;
    $("query").placeholder = copy.placeholder;
    $("submit").textContent = copy.button;
    renderExamples();
    renderEmpty();
  }

  function renderExamples() {
    const box = $("examples");
    box.replaceChildren(...(examples[mode] || []).map((ex) =>
      el("button", { class: "chip-example", type: "button", title: ex.text, onclick: () => { $("query").value = ex.text; $("query").focus(); } }, ex.label)));
  }

  function renderEmpty() {
    const copy = MODE_COPY[mode];
    $("results").replaceChildren(el("div", { class: "empty" },
      el("p", { class: "empty-title", text: copy.emptyTitle }), el("p", { text: copy.emptyText })));
  }

  // ------------------------------------------------------------------ ask
  async function submit() {
    const text = $("query").value.trim();
    if (busy || text.length < 3) return;
    busy = true;
    $("submit").disabled = true;
    const spinner = $("spinner-tpl").content.cloneNode(true);
    $("results").replaceChildren(spinner);
    const started = Date.now();
    const timer = setInterval(() => {
      const s = Math.round((Date.now() - started) / 1000);
      const e = $("elapsed");
      if (e) e.textContent = `${s < 3 ? "Retrieving guidance" : mode === "determine" ? "Reading sources and determining tier" : "Reading sources"}… ${s}s`;
    }, 500);
    try {
      const result = await api(`/api/${mode}`, { text });
      renderResult(result);
    } catch (err) {
      $("results").replaceChildren(el("div", { class: "card" },
        el("div", { class: "warning", text: `Request failed: ${err.message}` })));
    } finally {
      clearInterval(timer);
      busy = false;
      $("submit").disabled = false;
    }
  }

  function confidence(level) {
    const n = CONF_LEVEL[level] || 0;
    return el("span", { class: "conf" }, "Confidence",
      el("span", { class: "conf-bars", "aria-label": `${level} confidence` }, [1, 2, 3].map((i) => el("span", { class: i <= n ? "on" : "" }))),
      level || "n/a");
  }

  function citeChip(c) {
    return el("button", { class: "cite", type: "button", title: c.citation, "data-label": c.label,
      onclick: () => focusSource(c.label) }, c.label);
  }

  function pointItem(p) {
    return el("li", { class: p.supported ? "" : "weak" },
      p.text, p.citations.map(citeChip),
      p.citations.length === 0 ? el("span", { class: "weak-note", text: "No valid citation: do not rely on this point." })
        : !p.supported ? el("span", { class: "weak-note", text: "Weakly supported by the cited text: check the source." }) : null);
  }

  function renderResult(r) {
    const card = el("div", { class: "card" });
    const verdict = el("div", { class: "verdict" });
    if (r.mode === "determine") {
      const tier = r.tier || "insufficient_information";
      verdict.append(el("span", { class: `tier-badge tier-${tier}` }, el("small", { text: "Tier" }), TIER_LABEL[tier] || tier));
    } else if (r.abstained) {
      verdict.append(el("span", { class: "tier-badge tier-insufficient_information", text: "Not covered" }));
    }
    verdict.append(confidence(r.confidence));
    if (r.needs_review) verdict.append(el("span", { class: "flag", text: "Needs review" }));
    card.append(verdict, el("p", { class: "summary", text: r.summary || r.abstain_reason || "" }));

    if (r.warnings && r.warnings.length) {
      card.append(el("div", { class: "warnings" }, r.warnings.map((w) => el("div", { class: "warning", text: w }))));
    }
    const groups = r.mode === "determine"
      ? [["reasoning", "Why"], ["required_measures", "What you need to do"]]
      : [["key_points", "Key points"]];
    for (const [key, title] of groups) {
      const pts = (r.points || []).filter((p) => p.group === key);
      if (pts.length) card.append(el("h3", { text: title }), el("ul", { class: "points" }, pts.map(pointItem)));
    }
    if (r.missing_information && r.missing_information.length) {
      card.append(el("h3", { text: "Information that would change or confirm this" }),
        el("ul", { class: "missing" }, r.missing_information.map((m) => el("li", { text: m }))));
    }

    const t = r.timings || {};
    const fb = el("span", { class: "feedback" }, "Was this helpful?",
      ...["helpful", "not_helpful"].map((v) => el("button", { type: "button", "data-v": v, onclick: (ev) => sendFeedback(r.query_id, v, ev.target) },
        v === "helpful" ? "Yes" : "No")));
    card.append(el("div", { class: "meta" },
      el("span", { text: `${(t.total_s || 0).toFixed(1)}s` }),
      el("span", { text: `Snapshot ${r.snapshot || "unknown"}` }),
      el("span", { text: (r.models && r.models.generator || "").replace("ollama:", "") }),
      r.checks && r.checks.citation_validity !== undefined ? el("span", { text: `Citation validity ${Math.round(r.checks.citation_validity * 100)}%` }) : null,
      r.query_id ? fb : null));

    const sources = r.sources || [];
    const cited = sources.filter((s) => s.cited);
    const uncited = sources.filter((s) => !s.cited);
    const srcCard = el("div", { class: "card" }, el("h3", { text: `Sources cited (${cited.length})`, style: "margin-top:0" }));
    const list = el("div", { class: "sources" }, cited.map(sourceItem));
    srcCard.append(cited.length ? list : el("p", { class: "muted", text: "No sources were cited." }));
    if (uncited.length) {
      const more = el("div", { class: "sources", hidden: true }, uncited.map(sourceItem));
      srcCard.append(el("button", { class: "uncited-toggle", type: "button", onclick: (ev) => {
        more.hidden = !more.hidden;
        ev.target.textContent = `${more.hidden ? "Show" : "Hide"} ${uncited.length} other retrieved passage${uncited.length > 1 ? "s" : ""}`;
      } }, `Show ${uncited.length} other retrieved passage${uncited.length > 1 ? "s" : ""}`), more);
    }
    $("results").replaceChildren(card, srcCard);
  }

  function sourceItem(s) {
    const details = el("details", { class: `source${s.cited ? " cited" : ""}`, id: `src-${s.label}` },
      el("summary", {},
        el("span", { class: "source-label", text: s.label }),
        el("span", {}, el("span", { class: "source-title", text: s.citation }),
          el("span", { class: "source-sub", text: s.heading_path }))),
      el("div", { class: "source-body" },
        el("div", { class: "source-text", text: s.text }),
        el("div", { class: "source-links" },
          s.url ? el("a", { href: s.url, target: "_blank", rel: "noopener noreferrer", text: "Open original ↗" }) : null,
          s.last_updated ? el("span", { text: `Page updated ${s.last_updated}` }) : null,
          el("span", { style: "font-family: var(--mono)", text: s.chunk_id }))));
    return details;
  }

  function focusSource(label) {
    const node = document.getElementById(`src-${label}`);
    if (!node) return;
    if (node.parentElement && node.parentElement.hidden) node.parentElement.hidden = false;
    node.open = true;
    node.scrollIntoView({ behavior: "smooth", block: "center" });
    node.classList.remove("flash");
    void node.offsetWidth;
    node.classList.add("flash");
  }

  async function sendFeedback(id, value, btn) {
    try {
      await api("/api/feedback", { query_id: id, value });
      btn.parentElement.querySelectorAll("button").forEach((b) => b.classList.toggle("chosen", b === btn));
    } catch (_) { /* non-critical */ }
  }

  // ------------------------------------------------------------------ gaps
  async function loadGaps() {
    let data;
    try { data = await api("/api/gaps"); } catch (err) {
      $("gaps-table").replaceChildren(el("tr", {}, el("td", { text: `Could not load: ${err.message}` })));
      return;
    }
    const s = data.summary;
    const tile = (v, l) => el("div", { class: "tile" }, el("div", { class: "tile-value", text: String(v) }), el("div", { class: "tile-label", text: l }));
    $("gap-tiles").replaceChildren(tile(s.total, "Questions asked"), tile(s.abstained, "Could not answer"),
      tile(s.needs_review, "Flagged for review"), tile(s.low_confidence, "Low confidence"));
    const head = el("tr", {}, ["When", "Mode", "Question", "Outcome", "Why flagged", "Feedback"].map((h) => el("th", { text: h })));
    const rows = data.items.map((q) => {
      const outcome = q.abstained ? "Could not answer" : q.tier ? TIER_LABEL[q.tier] || q.tier : "Answered";
      const cls = q.tier ? `pill tier-${q.abstained ? "insufficient_information" : q.tier}` : "pill tier-insufficient_information";
      return el("tr", {},
        el("td", { text: new Date(q.ts).toLocaleString() }),
        el("td", { text: q.mode }),
        el("td", { class: q.query ? "q" : "q muted", text: q.query || "(question not stored)" }),
        el("td", {}, el("span", { class: cls, text: outcome }), el("div", { class: "muted", text: q.confidence ? `${q.confidence} confidence` : "" })),
        el("td", { class: "muted", text: q.reason || "" }),
        el("td", { text: q.feedback ? q.feedback.replace("_", " ") : "" }));
    });
    $("gaps-table").replaceChildren(el("thead", {}, head),
      el("tbody", {}, rows.length ? rows : [el("tr", {}, el("td", { colspan: "6", class: "muted", text: "Nothing flagged yet." }))]));
  }

  // ------------------------------------------------------------------ init
  document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => setMode(t.dataset.tab)));
  $("submit").addEventListener("click", submit);
  $("refresh-gaps").addEventListener("click", loadGaps);
  $("query").addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) submit(); });
  api("/api/examples").then((ex) => { examples = ex; renderExamples(); }).catch(() => {});
  loadHealth();
  setMode("determine");
})();
