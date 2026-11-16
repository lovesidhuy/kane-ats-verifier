# Suite 53 — Kane triage (open bug, no live re-runs)

**Verdict:** **(a) Real harness bug Kane caught** — not a wrong `.testmd` assertion.

## Failure

Step 2 expects `dedupe-summary` labels (e.g. "Raw Scraped Leads") **after** clicking **Run JobsFarm Discovery Deduplication**. The UI calls `fetch('/api/run-dedupe', { method: 'POST' })` without JSON `Content-Type`; Flask returns **415 Unsupported Media Type**, so `#dedupe-summary` stays `hidden`.

## failure.yaml (step 1-1, live_b pack)

- **message:** Both POST requests return 415; result section remains hidden.
- **category:** `application_issue/api_error`
- **title:** Deduplication run request is rejected with unsupported media type

## Sealed packs (local paths, not in git)

| Run | Pack |
|-----|------|
| `v1_explore_53_live` | `~/.testmuai/.../0b372879.../51420380-ca49-4022-babf-b7b7538086ee.evidence` |
| `v1_explore_53_live_b` | `~/.testmuai/.../45b0c9cd.../a63d9e1e-3b1c-419b-bd9f-cc26bdc60011.evidence` |

Judges: `kane-cli evidence serve <path>` on this Mac.

## Status

**Keep suite red.** Fix belongs in harness `runDedupe()` (add headers/body), not in spec cheat and not gated on passing suite 53.