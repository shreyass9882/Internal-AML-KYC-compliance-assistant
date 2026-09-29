"""FastAPI server: JSON API + a static single-page UI."""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from amlrag.config import Config
from amlrag.querylog import QueryLog

log = logging.getLogger(__name__)
STATIC = Path(__file__).parent / "static"

EXAMPLES = {
    "determine": [
        {"label": "Foreign PEP", "text": "An individual customer tells us she is a serving deputy minister of finance "
                                         "in a foreign country and wants to open a savings account."},
        {"label": "Café company", "text": "An Australian proprietary company that runs a café opens a business "
                                          "account. Two directors own 50% each. Medium risk, no PEP matches."},
        {"label": "Government dept", "text": "A Commonwealth government department opens an account to receive "
                                              "fees. We rate the ML/TF risk as low."},
        {"label": "SMSF", "text": "The trustees of an ATO-registered self-managed super fund ask us not to identify "
                                  "the fund's beneficial owners because it is regulated. Risk is low."},
    ],
    "explain": [
        {"label": "SoW vs SoF", "text": "What is the difference between source of wealth and source of funds?"},
        {"label": "Trust KYC", "text": "What KYC information do we need to collect for a trust customer?"},
        {"label": "Delayed CDD", "text": "When can we delay verifying a customer's identity?"},
        {"label": "ECDD triggers", "text": "What situations make enhanced customer due diligence mandatory?"},
    ],
}


class AskRequest(BaseModel):
    text: str = Field(min_length=3, max_length=4000)


class FeedbackRequest(BaseModel):
    query_id: int
    value: Literal["helpful", "not_helpful"]


def create_app(cfg: Config, assistant=None) -> FastAPI:
    app = FastAPI(title="AML/CTF CDD Compliance Assistant", version="0.1.0")
    qlog = QueryLog(cfg.path("query_log"))
    state: dict[str, Any] = {"assistant": assistant, "error": None}
    lock = threading.Lock()

    def get_assistant():
        if state["assistant"] is None:
            with lock:
                if state["assistant"] is None:
                    from amlrag.pipeline import Assistant

                    try:
                        state["assistant"] = Assistant.from_config(cfg)
                        state["error"] = None
                    except Exception as exc:
                        state["error"] = str(exc)
                        raise HTTPException(503, f"Assistant not ready: {exc}") from exc
        return state["assistant"]

    def run(mode: str, req: AskRequest) -> dict[str, Any]:
        a = get_assistant()
        result = a.ask(mode, req.text)
        result["query_id"] = qlog.record(result)
        return result

    @app.post("/api/determine")
    def determine(req: AskRequest) -> dict[str, Any]:
        return run("determine", req)

    @app.post("/api/explain")
    def explain(req: AskRequest) -> dict[str, Any]:
        return run("explain", req)

    @app.post("/api/feedback")
    def feedback(req: FeedbackRequest) -> dict[str, Any]:
        if not qlog.feedback(req.query_id, req.value):
            raise HTTPException(404, "unknown query id")
        return {"ok": True}

    @app.get("/api/gaps")
    def gaps(limit: int = 200) -> dict[str, Any]:
        return {"summary": qlog.summary(), "items": qlog.gaps(limit)}

    @app.get("/api/examples")
    def examples() -> dict[str, Any]:
        return EXAMPLES

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        try:
            a = get_assistant()
        except HTTPException:
            return {"ok": False, "error": state["error"]}
        manifest = a.retriever.store.manifest
        return {"ok": True, "snapshot": a.snapshot, "chunks": manifest.get("chunks"),
                "embedder": a.embedder_name, "generator": getattr(a.llm, "name", "?"),
                "offline_stub": a.offline_stub, "built_at": manifest.get("built_at")}

    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    return app
