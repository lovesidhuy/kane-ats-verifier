---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/ashby?persona=international_coop&variant=mutated_ids
tags: [tier2, persona, international-coop, ashby]
max_steps: 25
---

# Tier 2 Persona Matrix — International Co-op on Mutated Ashby

## Step 1: Open Mutated Ashby Form
Navigate to http://127.0.0.1:8766/ats/ashby?persona=international_coop&variant=mutated_ids.
Assert that "persona=international_coop" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "fld_9a1x" has value "Arjun".
Assert that select with id "fld_5h9r" has value "Yes".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
