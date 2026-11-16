---
mode: testing
target: chrome
url: http://127.0.0.1:8766/tools/qa-bank
tags: [tier2, qa-bank, policy, visa]
max_steps: 20
---

# Tier 2 QA Bank — Visa Sponsorship Policy Verification

## Step 1: Open QA Bank Tester & Select Visa Sponsorship
Navigate to http://127.0.0.1:8766/tools/qa-bank.
Click the button "Visa Sponsorship".
Click the button "Resolve Answer from JobsFarm QA Bank".

## Step 2: Verify Deterministic Policy Output
Assert that "No" is visible in the QA result panel.
Assert that "policy" is visible in the source field.
