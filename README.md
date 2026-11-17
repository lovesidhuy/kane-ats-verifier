# Kane ATS Verifier — Closed-Loop Browser Verification

<p align="center">
  <strong>An agent that fills job applications on any ATS; Kane CLI proves it never submits a broken one — turning every green run into verified training data.</strong>
</p>

## Technical Documentation & Architecture

| Doc | Purpose |
|-----|---------|
| [VERIFICATION.md](VERIFICATION.md) | **0-credit** verification replay path (`doctor` + `demo`) & credentials guide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture & system capabilities (Engine, Verification, Closed-Loop, Tooling) |
| [SPECIFICATION.md](SPECIFICATION.md) | Verification claims-to-evidence matrix & platform specification |
| [KANE_CAUGHT.md](KANE_CAUGHT.md) | Real regressions caught and triaged by Kane CLI (incl. K-16 dedupe 415 and CL-2 visa seed) |
| [DATASET_CARD.md](DATASET_CARD.md) | 190-trajectory reward-filtered browser agent dataset card |
| [SCOPE.md](SCOPE.md) | Verification boundaries & security safeguards |

## Clean Standalone Verification Architecture

This repository is a clean, standalone verification system:
- `ats_verifier/` — standalone DOM autofill engine, deterministic QA policy resolver, and discovery deduplicator (no legacy code, no proxies, no CAPTCHA solvers).
- `tests/kane/harness.py` — local multi-ATS & multi-persona verification server (`127.0.0.1:8766`, dry-run + network no-submit guard).
- `scripts/kane_loop.py` — closed-loop runner: executes Kane CLI, parses NDJSON + `failure.yaml`, emits a `FixPlan`, writes `tests/kane/.loop_agent_policy.json`, and retries until Kane passes.
- `tests/` — **42** pytest unit/integration tests and **54** indexed `.testmd` suites.
- `evidence/` — **45** sealed `.evidence` packs, **24** recorded loop runs, and **190** reward-filtered trajectories (**50** public sample).
- Credits recorded in `evidence/credits_ledger.csv`: **1119.31** ledger sum (**1742.05** balance delta).

## Unified CLI & 0-credit demo

Run the entire verification suite, replay the closed-loop agent repair, inspect pre-submit boundary receipts, or audit dataset trajectories with a single zero-dependency CLI command:

```bash
git clone https://github.com/lovesidhuy/kane-ats-verifier.git
cd kane-ats-verifier
python3 -m pip install -r requirements.txt

# Unified Developer CLI:
./kane-ats demo          # Offline replay + 42 pytest + claims check; reports elapsed time
./kane-ats heal          # Closed-loop red -> heuristic rule fix -> green with visual diff
./kane-ats receipts      # Inspect preflight HTML5/ARIA compliance receipts
./kane-ats dataset-stats # 190-trajectory dataset validation & distribution
./kane-ats audit         # Full integrity audit & claims verification
```

Or via the classic shell entrypoint:
```bash
./scripts/run_kane_verify.sh doctor
./scripts/run_kane_verify.sh demo
python3 scripts/check_claims.py
```

Artifacts: `evidence/loop_runs/judge_demo/summary.json` (replay **red → fix → green**), `evidence/receipts/` (preflight compliance receipts).

## Scope & Safety Safeguards

- **In scope:** `ats_verifier/`, `tests/kane/`, `scripts/kane_loop.py`, `evidence/`.
- **Out of scope:** CAPTCHA solving, residential proxies, anti-detect browsers, and real-employer form submission — see [SCOPE.md](SCOPE.md).

## License

AGPL-3.0 — see [LICENSE](LICENSE).

## Official evidence and local reruns

24 recorded loop runs (11 live Kane CLI loop runs, 4 replays, 8 standalone live-suite runs, and 1 blocked CLI attempt).

These are recorded attempts, not 24 passing live loops. The committed `evidence/loop_runs/MANIFEST.json` lists each run, a descriptive label, its type and its summary SHA-256. The locked/authentication-denied attempt is counted separately from live verification. `e6e9accfb444` is a labeled archived fixture replay; `4a5fa1d6f3b1` has no committed summary and is excluded.

`demo`, `heal`, and `loop` write diagnostics and runtime receipts only under ignored `evidence/local_runs/`. They never regenerate the official index or `SUBMISSION.json`; `check_claims.py` is read-only by default. Repeated judge runs do not change official counts.

Archiving is an explicit maintainer operation: `python3 scripts/kane_loop.py --replay --save-evidence --official --run-id new_descriptive_name`. Existing official run directories cannot be overwritten. Review and add the new summary to `MANIFEST.json` with its type, label and SHA-256 before explicitly running `python3 scripts/evidence_index.py` and `python3 scripts/check_claims.py --write-submission`, then commit the reviewed changes. Merely saving a folder does not change the claims count.
