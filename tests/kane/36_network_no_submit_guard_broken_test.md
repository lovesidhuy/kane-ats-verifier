---
mode: testing
target: chrome
url: http://127.0.0.1:8766/tools/network-guard-test?guard=off
tags: [tier2, safety, network-guard, negative, p0-3]
max_steps: 15
---

# P0-3 Network Guard NEGATIVE (guard disabled — must fail if guard works)

> Run only with guard intentionally off (`?guard=off`). If the guard is on, this suite should **fail** (proves the positive suite is meaningful).

## Step 1: Open disabled guard probe
Navigate to http://127.0.0.1:8766/tools/network-guard-test?guard=off.
Assert that "NETWORK_SUBMIT_GUARD_DISABLED" is visible.

## Step 2: Probe external POST without guard
Click the button "Probe external application POST".

## Step 3: Expect no block banner (negative)
Assert that "NETWORK_SUBMIT_GUARD_BLOCKED" is not visible.
Assert that "PROBE_UNBLOCKED_OK" is visible or "PROBE_SENDING" is visible.