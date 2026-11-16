---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/bamboohr?persona=qa_automation&variant=mutated_ids
tags: [tier2, persona, qa-automation, mutated-dom, bamboohr]
max_steps: 25
---

# Tier 2 Persona Matrix — QA Automation Engineer on Mutated BambooHR

## Step 1: Open Mutated BambooHR Form
Navigate to http://127.0.0.1:8766/ats/bamboohr?persona=qa_automation&variant=mutated_ids.
Assert that "persona=qa_automation" and "variant=mutated_ids" are visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Mutated Fields & Safety Guard
Assert that input with id "fld_9a1x" has value "Hannah".
Assert that input with id "fld_3c4m" has value "hannah.kim@example.com".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
