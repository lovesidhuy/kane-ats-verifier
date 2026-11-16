---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/workopolis?persona=healthcare_ops&variant=mutated_ids
tags: [tier2, persona, healthcare-ops, mutated-dom, workopolis]
max_steps: 25
---

# Tier 2 Persona Matrix — Healthcare Ops on Mutated Workopolis

## Step 1: Open Mutated Workopolis Form
Navigate to http://127.0.0.1:8766/ats/workopolis?persona=healthcare_ops&variant=mutated_ids.
Assert that "persona=healthcare_ops" and "variant=mutated_ids" are visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Mutated Fields & Safety Guard
Assert that input with id "fld_9a1x" has value "Marcus".
Assert that input with id "fld_3c4m" has value "marcus.vance@example.com".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
