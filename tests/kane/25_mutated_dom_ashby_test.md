---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/ashby?persona=senior_fullstack&variant=mutated_ids
tags: [tier2, mutated-dom, ashby]
max_steps: 25
---

# Tier 2 Mutated DOM — Senior Full-Stack on Ashby

## Step 1: Open Mutated Ashby Form
Navigate to http://127.0.0.1:8766/ats/ashby?persona=senior_fullstack&variant=mutated_ids.
Assert that "variant=mutated_ids" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Mutated Fields & Safety Guard
Assert that input with id "fld_9a1x" has value "Jane".
Assert that input with id "fld_3c4m" has value "user@example.com".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
