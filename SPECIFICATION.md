# Kane ATS Verifier — Closed-Loop ATS Verification Specification

**Overview:** This is a clean, standalone verification system. All application code (`ats_verifier/`), verification harness (`tests/kane/harness.py`), closed loop (`scripts/kane_loop.py`), suites (`tests/kane/`), and sealed packs (`evidence/`) live in this repository.

## One-liner

An autofill agent cannot ship a broken application: **Kane CLI** runs the `.testmd` suite, failures become a **FixPlan**, and the agent patches or writes a policy override (`tests/kane/.loop_agent_policy.json`) until Kane passes.

## One command (0 credits, no login)

```bash
./scripts/run_kane_verify.sh demo
```

Preflight from a clean clone:

```bash
./scripts/run_kane_verify.sh doctor
```

## Closed loop (recorded CL-2, requires Kane login for live)

```bash
./scripts/run_kane_verify.sh loop --live \
  --seed-bug visa_wrong_answer \
  --suite tests/kane/17_persona_visa_ashby_strict_test.md \
  --max-attempts 2 --credit-budget 60 \
  --save-evidence --run-id cl2_visa_seed_live
```

Evidence: `evidence/loop_runs/cl2_visa_seed_live/summary.json` (attempt 1 **`failed`**, attempt 2 **`passed`**, seed **still active**, agent policy file fixes sponsorship).

## What we do **not** ship

CAPTCHA solvers, residential proxies, anti-detect browsers, stealth plugins, or real external form submissions are **explicitly out of scope** (`SCOPE.md`).

## Claims ↔ evidence

Canonical headline numbers: **`python3 scripts/check_claims.py`** → `SUBMISSION.json`.

| Claim | Proof |
|-------|--------|
| **54** suites indexed | `evidence/evidence_index.json` |
| **42** pytest tests | `./kane-ats demo` (or `./scripts/run_kane_verify.sh demo`) |
| **45** sealed packs | `evidence/*.evidence` |
| **190** trajectories (**50** sample) | `evidence/dataset_manifest.json` |
| **24** recorded run entries | `evidence/loop_runs/MANIFEST.json` |
| Credits **1119.31** ledger Σ · **1742.05** balance Δ | `evidence/credits_ledger.csv` |
| Closed loop red→fix→green | `evidence/loop_runs/cl2_visa_seed_live/` |
| Kane caught real bugs | `KANE_CAUGHT.md` (K-16 dedupe 415 fixed; CL-2 visa seed) |
| Network no-submit guard | `tests/kane/36_network_no_submit_guard_test.md` |

See `VERIFICATION.md` for credentials, replay fallback, and FAQ.
