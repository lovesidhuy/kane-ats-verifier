# Hackathon scope boundary (P0-4)

This repo is a standalone **closed-loop browser verification artifact** built for the KaneCLI Online Hackathon (Nov 12–19, 2026).

## Included in judging

- `ats_verifier/` — standalone DOM autofill, deterministic QA policy resolver, and discovery deduplicator
- `tests/kane/harness.py` — local ATS matrix (7 ATS × 10 personas × 4 variants), dry-run only, network submit guard
- `scripts/kane_loop.py` — closed loop + `.loop_agent_policy.json` overrides + replay
- `scripts/run_kane_verify.sh` — `demo`, `doctor`, `loop`
- `evidence/` — 23 sealed `.evidence` packs, 18 loop runs, 50-row trajectory sample, CL-2 showcase
- Hackathon docs: `README_KANE_HACKATHON.md`, `KANE_CAUGHT.md`, `JUDGES.md`, `DATASET_CARD.md`, `docs/SUBMISSION_FORM.md`

## Explicitly excluded

- CAPTCHA solving
- Proxy ladders / residential proxies
- Anti-detect browsers or stealth plugins
- Real-employer form submission (all verification runs against `http://127.0.0.1:8766` or dry-run boards without final submit)
