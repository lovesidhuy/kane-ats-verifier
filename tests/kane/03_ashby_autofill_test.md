---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/ashby
tags: [ats, ashby, autofill, safety-guard]
max_steps: 25
---

# JobsFarm Ashby ATS DOMAutofill & Safety Guard Verification

## Step 1: Open Ashby ATS Target
Navigate to http://127.0.0.1:8766/ats/ashby.
Assert the heading "AI Systems & Automation Engineer" is visible.
Assert that "VectorScale AI" and "AS-2026-9012" are visible.

## Step 2: Execute Untouched JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that the status badge updates to include "AUTOFILL_COMPLETED".

## Step 3: Verify Populated Fields & Safety Guard
Assert that input with id "first_name" has value "Jane".
Assert that select with id "work_auth" has value "Yes".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
