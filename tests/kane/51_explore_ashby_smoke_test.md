---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/ashby
tags: [explore, ashby, v1]
max_steps: 15
---

# Explore regression — Ashby layout

## Step 1
Navigate to http://127.0.0.1:8766/ats/ashby.
Assert that "Ashby ATS" is visible.

## Step 2
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible.