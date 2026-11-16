# CL-2 showcase — **deliberately planted** `visa_wrong_answer`

> **Planted bug (not a production defect):** With `--seed-bug visa_wrong_answer`, the harness answers `sponsorship=No` for persona `visa_sponsorship`. Suite `17_persona_visa_ashby_strict` expects **`Yes`**. Kane **fails** attempt 1; the **agent** reads Kane’s mismatch and writes `policy_override` to `tests/kane/.loop_agent_policy.json` (seed **stays active**); attempt 2 passes with agent-corrected fill.

## Run (live, harness on `:8766`)

```bash
./scripts/run_kane_verify.sh loop --live \
  --seed-bug visa_wrong_answer \
  --suite tests/kane/17_persona_visa_ashby_strict_test.md \
  --max-attempts 2 \
  --credit-budget 150 \
  --save-evidence \
  --run-id cl2_visa_seed_live
```

Requires `kane-cli login` (or `LT_USERNAME` / `LT_ACCESS_KEY`). Flags on `testmd run` confirmed via `kane-cli testmd run --help` (`--agent`, `--headless`, `--timeout`, `--username`, `--access-key`).

## Expected loop behavior

| Attempt | Seed active? | Expected Kane `overall_status` | FixPlan |
|---------|--------------|-------------------------------|---------|
| 1 | yes | `failed` (sponsorship assertion) | — |
| 2 | **yes** (seed still planted) | `passed` | `policy_override` → agent file `sponsorship=Yes` |

Artifacts: `evidence/loop_runs/<run_id>/summary.json` and `attempt_*/kane.ndjson`.

## Recorded run (2026-11-14, local Mac)

| Field | Value |
|-------|--------|
| `run_id` | `cl2_visa_seed_live` |
| Attempt 1 `test_md_done.overall_status` | **`failed`** (sponsorship `No` vs expected `Yes`) |
| Attempt 2 `test_md_done.overall_status` | **`passed`** |
| Fix between attempts | `agent_policy_override_applied` (`tests/kane/.loop_agent_policy.json`) |
| Attempt 2 `seed_bug_active` | **`visa_wrong_answer`** (agent fix, not seed removal) |
| Credits (balance delta) | **~39.6** (`7881.31` → `7841.74`, honest rerun) |

Proof paths:

- `evidence/loop_runs/cl2_visa_seed_live/attempt_1/kane.ndjson` — failed assertion on `sponsorship`
- `evidence/loop_runs/cl2_visa_seed_live/attempt_2/kane.ndjson` — `"overall_status":"passed"`
- `evidence/loop_runs/cl2_visa_seed_live/fixplan.json` (via `attempt_1/fixplan.json`)

## Local proof without credits

```bash
pytest tests/test_kane_loop.py::test_seed_bug_visa_wrong_answer_plants_no_sponsorship -v
```