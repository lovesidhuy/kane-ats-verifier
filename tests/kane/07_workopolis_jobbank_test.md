---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/workopolis
tags: [portal, workopolis, jobbank, autofill]
max_steps: 25
---

# JobsFarm Workopolis & Job Bank Canada DOMAutofill Verification

## Step 1: Open Workopolis Target
Navigate to http://127.0.0.1:8766/ats/workopolis.
Assert the heading "Technical Support Engineer (Tier 2)" is visible.
Assert that "MapleLeaf Digital" and "WK-2026-1198" are visible.

## Step 2: Execute Untouched JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that the status badge updates to include "AUTOFILL_COMPLETED".

## Step 3: Verify Populated Fields & Safety Guard
Assert that input with id "first_name" has value "Jane".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
