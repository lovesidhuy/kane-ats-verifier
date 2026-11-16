---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/indeed
tags: [portal, indeed, smartapply, autofill]
max_steps: 25
---

# JobsFarm Indeed SmartApply DOMAutofill Verification

## Step 1: Open Indeed SmartApply Target
Navigate to http://127.0.0.1:8766/ats/indeed.
Assert the heading "Network & Security Specialist" is visible.
Assert that "Pacific Telco Corp" and "IN-2026-5509" are visible.

## Step 2: Execute Untouched JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that the status badge updates to include "AUTOFILL_COMPLETED".

## Step 3: Verify Populated Fields & Safety Guard
Assert that input with id "first_name" has value "Jane".
Assert that select with id "work_auth" has value "Yes".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
