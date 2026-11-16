# CL-4 — Loop stats across seeded bug types

| Seed | Suite | Attempts | Outcome | Credits (recorded) | Fix action |
|------|-------|----------|---------|-------------------|------------|
| `visa_wrong_answer` | `17_persona_visa_ashby_strict_test.md` | 2 | pass | **39.57** | `agent_policy_override_applied` |
| (replay) list-index | fixtures `red.ndjson` → `green.ndjson` | 2 | pass | **0** | `harness_patch` |
| (replay) env lock | `broken.ndjson` | 1 | stop | **0** | `needs_human` / env |

**Planned seeds (not all live-run):** `email_wrong_answer`, `salary_wrong_answer` — same loop path via `policy_override` / `set_value` FixPlan kinds.

Command template:

```bash
python3 scripts/kane_loop.py --live --seed-bug <name> --suite <suite> --max-attempts 2 --credit-budget 60 --save-evidence
```