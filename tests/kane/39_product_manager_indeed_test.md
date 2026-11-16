---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/indeed?persona=product_manager&variant=mutated_ids
tags: [tier2, persona, product-manager, indeed]
max_steps: 25
---

# Tier 2 Persona Matrix — Product Manager on Mutated Indeed

## Step 1: Open Mutated Indeed Form
Navigate to http://127.0.0.1:8766/ats/indeed?persona=product_manager&variant=mutated_ids.
Assert that "persona=product_manager" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "fld_9a1x" has value "Liam".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
