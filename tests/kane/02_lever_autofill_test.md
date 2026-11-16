---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/lever
tags: [ats, lever, autofill, safety-guard]
max_steps: 25
---

# JobsFarm Lever ATS DOMAutofill & Safety Guard Verification

## Step 1: Open Lever ATS Target
Navigate to http://127.0.0.1:8766/ats/lever.
Assert the heading "Platform Reliability Engineer" is visible.
Assert that "Apex Systems Labs" and "LV-2026-7821" are visible.

## Step 2: Execute Untouched JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that the status badge updates to include "AUTOFILL_COMPLETED".

## Step 3: Verify Populated Fields from Candidate Profile & QA Bank
Assert that input with id "first_name" has value "Jane".
Assert that input with id "last_name" has value "Doe".
Assert that select with id "work_auth" has value "Yes".
Assert that select with id "sponsorship" has value "No".

## Step 4: Verify Dry-Run Safety Guard
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
