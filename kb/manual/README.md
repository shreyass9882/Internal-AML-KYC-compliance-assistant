# Manually placed sources

Files here override the URL in `kb/sources.yaml` for the document with the same id. Run `amlrag fetch` after adding a file so it is recorded (with its sha256) in `kb/snapshot.lock.json`.

| File | Source |
|---|---|
| `rules2025.pdf` | *Anti-Money Laundering and Counter-Terrorism Financing Rules 2025* (F2025L01026), Compilation No. 1 (F2026C00274, 31 March 2026), which includes the 2026 amendments. PDF from <https://www.legislation.gov.au/F2025L01026/2026-03-31/downloads>. A text export saved as `rules2025.txt` also works. The version must match `url` in `kb/sources.yaml`, since citations link there. |
| `amlctf-act.pdf` | *(optional)* Latest compilation of the *Anti-Money Laundering and Counter-Terrorism Financing Act 2006* (C2006A00169) from <https://www.legislation.gov.au/C2006A00169/latest/downloads>. |
| `<id>.html` | Any AUSTRAC page the fetcher can't download (save the page from a browser as "HTML only"). |

Record in the final report which compilation (compilation number and date shown on the PDF's cover) the snapshot uses.
