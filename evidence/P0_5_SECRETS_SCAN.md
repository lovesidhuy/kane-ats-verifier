# P0-5 secrets & size scan (working tree)

Run: `python3 scripts/scan_secrets.py`

## Policy

- Scan scope: **repository paths** (`ats_verifier/`, `tests/`, `scripts/`, `evidence/`, docs).
- `.testmuai/` and `.env` are gitignored and must not be committed.
- Committed `.evidence` packs: **23** under `evidence/` (no API keys in repo grep).

## Result (2026-11-14)

| Check | Result |
|-------|--------|
| Secret patterns in repository paths | **0 hits** (after skipping vendor trees) |
| Files &gt; 5MB in repo | large media/trajectories gitignored or sample only |
| `SUBMISSION.json` / ledger | no credentials |

If `scan_secrets.py` exits non-zero, inspect `evidence/p0_5_secrets_scan.json` locally (gitignored).