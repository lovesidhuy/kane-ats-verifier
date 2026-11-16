---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/lever?persona=data_engineer&variant=mutated_ids
tags: [tier2, persona, data-engineer, mutated-dom, lever]
max_steps: 25
---

# Tier 2 Persona Matrix — Data Engineer on Mutated Lever

## Step 1: Open Mutated Lever Form for Data Engineer
Navigate to http://127.0.0.1:8766/ats/lever?persona=data_engineer&variant=mutated_ids.
Assert that "persona=data_engineer" and "variant=mutated_ids" are visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Mutated Fields & Safety Guard
Assert that input with id "fld_9a1x" has value "Sofia".
Assert that input with id "fld_3c4m" has value "sofia.mendez@example.com".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
