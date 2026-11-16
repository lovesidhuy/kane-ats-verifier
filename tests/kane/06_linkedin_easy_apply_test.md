---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/linkedin
tags: [portal, linkedin, easy-apply, autofill]
max_steps: 25
---

# JobsFarm LinkedIn Easy Apply DOMAutofill Verification

## Step 1: Open LinkedIn Easy Apply Target
Navigate to http://127.0.0.1:8766/ats/linkedin.
Assert the heading "DevOps & AWS Solutions Engineer" is visible.
Assert that "Horizon FinTech" and "LI-2026-6632" are visible.

## Step 2: Execute Untouched JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Populated Fields & Safety Guard
Assert that input with id "first_name" has value "Jane".
Assert that select with id "sponsorship" has value "No".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
