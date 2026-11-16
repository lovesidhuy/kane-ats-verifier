---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/greenhouse
tags: [ats, greenhouse, autofill, safety-guard]
max_steps: 25
---

# JobsFarm Greenhouse ATS DOMAutofill & Safety Guard Verification

## Step 1: Open Greenhouse ATS Target
Navigate to http://127.0.0.1:8766/ats/greenhouse.
Assert the heading "Senior Cloud Infrastructure Engineer" is visible.
Assert that "NorthStar Cloud Inc." and "GH-2026-4410" are visible.

## Step 2: Execute Untouched JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Populated Fields from Candidate Profile & QA Bank
Assert that input with id "first_name" has value "Jane".
Assert that input with id "last_name" has value "Doe".
Assert that input with id "email" has value "user@example.com".
Assert that select with id "work_auth" has value "Yes".
Assert that select with id "sponsorship" has value "No".

## Step 4: Verify Dry-Run Safety Guard
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
Assert that "Dry-Run Guard: Form prepared & verified, external POST aborted." is visible.
