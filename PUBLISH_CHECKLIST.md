# Publish checklist

## Pre-publish verification

- [x] Standalone artifact initialized cleanly (zero pre-Nov-12 legacy code)
- [x] `python3 scripts/check_claims.py` → `ok: true`
- [x] `./scripts/run_kane_verify.sh doctor` and `./scripts/run_kane_verify.sh demo` pass cleanly
- [x] `python3 scripts/scan_secrets.py` → 0 secret hits
- [x] `evidence/verified_trajectories_full_100.jsonl` excluded / gitignored
- [x] Fresh git repository initialized Nov 15, 2026 (no old August history, no secrets)

## Push new public GitHub repo

Create an empty public repo on GitHub (for example `lovesidhuy/kane-ats-verifier`), then run:

```bash
cd kane-ats-verifier
git remote add origin https://github.com/lovesidhuy/kane-ats-verifier.git
git branch -M main
git push -u origin main
```

## Remaining operator items before submitting form

- [x] Push `kane-ats-verifier` to a **new public GitHub repo** (created on or after Nov 12, 2026) -> https://github.com/lovesidhuy/kane-ats-verifier
- [ ] Record 3–5 min YouTube demo (`DEMO_SCRIPT.md`)
- [ ] Publish at least 2 public posts (`SOCIAL_POSTS.md`) on X / LinkedIn / HN / Reddit
- [ ] Submit at `https://www.kaneclihack.sh/o/submit` using `SUBMISSION_FORM.md`
