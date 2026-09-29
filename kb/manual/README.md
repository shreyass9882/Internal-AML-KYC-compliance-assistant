# Manually placed sources

Files here override the URL in `kb/sources.yaml` for the document with the same id. Run `amlrag fetch` after adding a file so it is recorded (with its sha256) in `kb/snapshot.lock.json`.

| File | Source |
|---|---|
| `rules2025.pdf` | Latest compilation of the *Anti-Money Laundering and Counter-Terrorism Financing Rules 2025* (F2025L01026), including the 2026 amendments. Download the PDF from <https://www.legislation.gov.au/F2025L01026/latest>. |
| `amlctf-act.pdf` | *(optional)* Latest compilation of the *Anti-Money Laundering and Counter-Terrorism Financing Act 2006* (C2004A01550) from <https://www.legislation.gov.au/C2004A01550/latest>. |
| `<id>.html` | Any AUSTRAC page the fetcher can't download (save the page from a browser as "HTML only"). |

Record in the final report which compilation (compilation number and date shown on the PDF's cover) the snapshot uses.
