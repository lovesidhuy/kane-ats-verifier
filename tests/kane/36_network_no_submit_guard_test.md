---
mode: testing
target: chrome
url: http://127.0.0.1:8766/tools/network-guard-test
tags: [tier2, safety, network-guard, p0-3]
max_steps: 15
---

# P0-3 Network No-Submit Guard (harness hosts only)

## Step 1: Open guard probe page
Navigate to http://127.0.0.1:8766/tools/network-guard-test.
Assert that "P0-3 network no-submit guard probe" is visible.

## Step 2: Trigger synthetic external POST
Click the button "Probe external application POST".

## Step 3: Verify network-level block
Assert that "NETWORK_SUBMIT_GUARD_BLOCKED" is visible.
Assert that "boards.greenhouse.io" is visible on the page.