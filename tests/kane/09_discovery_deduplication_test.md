---
mode: testing
target: chrome
url: http://127.0.0.1:8766/tools/discovery-dedupe
tags: [discovery, normalizer, deduplication]
max_steps: 25
---

# JobsFarm Two-Stage Discovery & Deduplication Verification

## Step 1: Open Discovery Deduplicator
Navigate to http://127.0.0.1:8766/tools/discovery-dedupe.
Assert the heading "JobsFarm Discovery Normalizer & Deduplicator" is visible.

## Step 2: Execute Deduplication Pipeline
Click the button "Run JobsFarm Discovery Deduplication".
Assert that element with id "raw-count" displays "5".
Assert that element with id "unique-count" displays "3".
Assert that element with id "removed-count" displays "2".
Assert that "NorthStar Cloud" and "Apex Systems" and "Cascadia Health" are visible.
