---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/linkedin?persona=data_engineer&variant=standard
tags: [tier2, persona, data-engineer, linkedin]
max_steps: 25
---

# Tier 2 Persona Matrix — Data Engineer on LinkedIn Easy Apply

## Step 1: Open LinkedIn Form
Navigate to http://127.0.0.1:8766/ats/linkedin?persona=data_engineer&variant=standard.
Assert that "persona=data_engineer" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "first_name" has value "Sofia".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
