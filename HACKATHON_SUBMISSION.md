# Kane ATS Verifier × Kane CLI — One-Page Submission

**One-liner:** An agent fills job applications on any ATS; **Kane CLI** proves the application is not broken before submit — green runs become verified browser-agent training data.

**0-credit proof:** `./scripts/run_kane_verify.sh doctor` then `./scripts/run_kane_verify.sh demo` → `evidence/loop_runs/judge_demo/summary.json`.

**Numbers (canonical):** `python3 scripts/check_claims.py` writes `SUBMISSION.json` from `evidence/evidence_index.json` + `evidence/dataset_manifest.json`.

| Claim | Artifact |
|-------|-----------|
| **54** Kane `.testmd` suites indexed | `evidence/evidence_index.json` |
| **35** standalone pytest tests (engine, loop, guard, mutation, K-16 API, pre-submit receipt, HF eval) | `.github/workflows/test.yml` / `demo` |
| **45** sealed `.evidence` packs in repo | `evidence/*.evidence` |
| **190** verified trajectories (**50** public sample) | `evidence/dataset_manifest.json`, `evidence/verified_trajectories_sample_50.jsonl` |
| **23** live/replay loop runs recorded | `evidence/loop_runs/*/summary.json` |
| Credits **1119.31** ledger Σ / **1742.05** balance Δ | `evidence/credits_ledger.csv` |

## 1. Ships (25%)

- Standalone `ats_verifier/` engine + local harness `tests/kane/harness.py` (10 personas × 7 ATS layouts × 4 DOM variants).
- Tier 1 live dry-runs: Greenhouse / Lever public boards (`tests/kane/11_*`, `12_*`).
- Network no-submit guard: `tests/kane/36_network_no_submit_guard_test.md`.

## 2. Verified (25%)

- Headline status per suite: `evidence/evidence_index.json` (parsed from `test_md_done.overall_status` / pack `result.yaml`).
- Exploration runs `v1_explore_50`–`54` under `evidence/loop_runs/`.
- Dataset export: `scripts/export_verified_trajectories.py`.

## 3. Closed loop (25%)

| Story | Evidence |
|-------|----------|
| CL-2 visa seed (live) | `evidence/loop_runs/cl2_visa_seed_live/` — attempt 1 **failed**, attempt 2 **passed**, seed still active |
| CL-4 email / salary seeds | `evidence/loop_runs/cl4_*_seed_live/` |
| K-16 dedupe 415 (fixed & verified by pytest) | `evidence/SUITE_53_KANE_TRIAGE.md`, `tests/test_discovery_dedupe_api.py` |

## 4. Craft (25%)

- `scripts/kane_loop.py` — `FixPlan`, replay, credits ledger, and `.loop_agent_policy.json` overrides.
- `KANE_CAUGHT.md` — regression map across K-01 through K-16.
- `docs/SUBMISSION_FORM.md` + `README.md` + `JUDGES.md` — zero-credit cold-clone verification path.
