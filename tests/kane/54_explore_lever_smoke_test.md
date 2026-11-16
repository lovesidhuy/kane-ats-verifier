---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/lever
tags: [explore, lever, v1]
max_steps: 15
---

# Explore regression — Lever layout

## Step 1
Navigate to http://127.0.0.1:8766/ats/lever.
Assert that "Lever ATS" is visible.

## Step 2
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible.