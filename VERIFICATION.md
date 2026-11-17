# Verification & Quickstart Guide

## Offline Verification Replay (No credentials, 0 credits)

Run with the unified `./kane-ats` CLI or shell entrypoint:

```bash
git clone https://github.com/lovesidhuy/kane-ats-verifier.git
cd kane-ats-verifier
python3 -m pip install -r requirements.txt

# One-command offline verification replay:
./kane-ats demo

# Interactive closed-loop repair replay with live heuristic rule diff:
./kane-ats heal

# Audit preflight HTML5/ARIA receipts & dataset:
./kane-ats receipts
./kane-ats dataset-stats
```

Or via the shell entrypoint:
```bash
./scripts/run_kane_verify.sh doctor
./scripts/run_kane_verify.sh demo
```

Artifacts: `evidence/loop_runs/judge_demo/summary.json` (replay red→fix→green on NDJSON fixtures).

**Timing:** `demo` measures and prints its elapsed time on your machine, including pytest, replay and the claims gate. No fixed runtime is promised.

| Metric | Source |
|--------|--------|
| **54** suites indexed | `SUBMISSION.json` |
| **42** standalone pytest tests | `demo` output |
| **45** sealed packs | `evidence_index.json` |
| **24** loop runs recorded | `evidence/loop_runs/` |
| **190** trajectories (**50** public sample) | `evidence/dataset_manifest.json` |
| Credits **1119.31** Σ / **1742.05** Δ | `credits_ledger.csv` |

## Live closed loop (optional)

Requires `npm i -g @testmuai/kane-cli` and:

```bash
export LT_USERNAME=...
export LT_ACCESS_KEY=...
kane-cli login --username "$LT_USERNAME" --access-key "$LT_ACCESS_KEY"
```

Then:

```bash
./scripts/run_kane_verify.sh loop --live \
  --seed-bug visa_wrong_answer \
  --suite tests/kane/17_persona_visa_ashby_strict_test.md \
  --max-attempts 2 --credit-budget 60 \
  --save-evidence --run-id cl2_visa_seed_live
```

Recorded artifact already in repo: `evidence/loop_runs/cl2_visa_seed_live/` (~40 credits, Nov 14 2026).

## If Kane auth fails

Use replay only (`demo`). Pass/fail is in `test_md_done.overall_status` inside `attempt_*/kane.ndjson`.

## Safety

- Harness only (`127.0.0.1:8766`) for loop/mutation; network guard blocks external POST.
- No real employer submits; `SAFETY_GUARD_ACTIVE` is UI dry-run only plus network guard.

## FAQ

| Question | Answer |
|----------|--------|
| Where is the engine? | Clean standalone `ats_verifier/` + `tests/kane/harness.py` + `scripts/kane_loop.py` |
| CAPTCHA/proxies? | **Out of scope / not included** — see `SCOPE.md` |
| Validate evidence zip? | Integrity only; use `overall_status` for pass/fail |
| Claims table | `SPECIFICATION.md` + `python3 scripts/check_claims.py` |

## Official evidence and local reruns

24 recorded loop runs (11 live Kane CLI loop runs, 4 replays, 8 standalone live-suite runs, and 1 blocked CLI attempt).

These are recorded attempts, not 24 passing live loops. The committed `evidence/loop_runs/MANIFEST.json` lists each run, a descriptive label, its type and its summary SHA-256. The locked/authentication-denied attempt is counted separately from live verification. `e6e9accfb444` is a labeled archived fixture replay; `4a5fa1d6f3b1` has no committed summary and is excluded.

`demo`, `heal`, and `loop` write diagnostics and runtime receipts only under ignored `evidence/local_runs/`. They never regenerate the official index or `SUBMISSION.json`; `check_claims.py` is read-only by default. Repeated judge runs do not change official counts.

Archiving is an explicit maintainer operation: `python3 scripts/kane_loop.py --replay --save-evidence --official --run-id new_descriptive_name`. Existing official run directories cannot be overwritten. Review and add the new summary to `MANIFEST.json` with its type, label and SHA-256 before explicitly running `python3 scripts/evidence_index.py` and `python3 scripts/check_claims.py --write-submission`, then commit the reviewed changes. Merely saving a folder does not change the claims count.
