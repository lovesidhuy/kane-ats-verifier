---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/bamboohr
tags: [ats, bamboohr, autofill, safety-guard]
max_steps: 25
---

# JobsFarm BambooHR ATS DOMAutofill & Safety Guard Verification

## Step 1: Open BambooHR ATS Target
Navigate to http://127.0.0.1:8766/ats/bamboohr.
Assert the heading "IT Systems Administrator" is visible.
Assert that "Cascadia Health Tech" and "BH-2026-3104" are visible.

## Step 2: Execute Untouched JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Populated Fields & Safety Guard
Assert that input with id "first_name" has value "Jane".
Assert that select with id "sponsorship" has value "No".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
