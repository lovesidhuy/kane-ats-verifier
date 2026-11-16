---
mode: testing
target: chrome
url: http://127.0.0.1:8766/tools/qa-bank
tags: [qa-bank, policy, answers]
max_steps: 25
---

# JobsFarm 7,300+ QA Bank & Policy Brain Verification

## Step 1: Open QA Bank Tester & Test Work Authorization
Navigate to http://127.0.0.1:8766/tools/qa-bank.
Assert the heading "JobsFarm QA Bank & Policy Resolution Tester" is visible.
Click the button "Resolve Answer from JobsFarm QA Bank".
Assert that element with id "qa-value" displays "Yes".
Assert that element with id "qa-source" displays "policy_auth_ca".

## Step 2: Test Visa Sponsorship Policy
Click the button "Visa Sponsorship".
Click the button "Resolve Answer from JobsFarm QA Bank".
Assert that element with id "qa-value" displays "No".
