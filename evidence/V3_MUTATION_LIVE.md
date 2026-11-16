# V-3 live mutation checks (fail → fix → pass)

| # | Mutation | Failed run (`test_md_done`) | Green after revert/fix | Credits (≈) |
|---|----------|----------------------------|------------------------|------------|
| 1 | Network guard **off** | `evidence/loop_runs/p0_3_suite36_broken_fail/` **failed** | Run with guard on: `p0_3_suite36_pass/` **passed** | 22 + 46 |
| 2 | `email_wrong_answer` seed | `cl4_email_seed_live/attempt_1` **failed** | `attempt_2` **passed** (agent `email=user@example.com`, seed still on) | 79 |
| 3 | `salary_wrong_answer` seed | `cl4_salary_seed_live/attempt_1` **failed** | `attempt_2` **passed** (agent `salary_expectation=160000`) | 43 |

Unit-level mutations (0 credits): `tests/test_mutation_check.py`.