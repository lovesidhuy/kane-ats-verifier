---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/lever?persona=security_analyst&variant=mutated_ids
tags: [tier2, persona, security-analyst, lever]
max_steps: 25
---

# Tier 2 Persona Matrix — Security Analyst on Mutated Lever

## Step 1: Open Mutated Lever Form
Navigate to http://127.0.0.1:8766/ats/lever?persona=security_analyst&variant=mutated_ids.
Assert that "persona=security_analyst" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "fld_9a1x" has value "Devon".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
