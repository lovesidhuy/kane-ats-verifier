#!/usr/bin/env bash
# Record a single kane-cli testmd run into evidence/loop_runs/<run_id>/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN_ID="${1:?run_id}"
SUITE="${2:?suite.md path}"
shift 2 || true
OUT="$ROOT/evidence/loop_runs/$RUN_ID"
mkdir -p "$OUT"
if ! curl -sf -o /dev/null "http://127.0.0.1:8766/ats/greenhouse" 2>/dev/null; then
  echo "Starting harness on :8766..."
  PYTHONPATH=. PORT=8766 python3 "$ROOT/tests/kane/harness.py" >>/tmp/ats_harness.log 2>&1 &
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
    curl -sf -o /dev/null "http://127.0.0.1:8766/ats/greenhouse" 2>/dev/null && break
    sleep 1
  done
fi
BEFORE=$(kane-cli balance 2>/dev/null | rg -o 'Available credits: [0-9.]+' || true)
set +e
kane-cli testmd run "$SUITE" --agent --headless --timeout 180 "$@" 2>&1 | tee "$OUT/kane.ndjson"
KANE_RC=${PIPESTATUS[0]}
set -e
AFTER=$(kane-cli balance 2>/dev/null | rg -o 'Available credits: [0-9.]+' || true)
python3 - "$OUT" "$SUITE" "$BEFORE" "$AFTER" <<'PY'
import json, re, sys
from pathlib import Path
out, suite, before, after = sys.argv[1:5]
def parse_bal(s):
    m = re.search(r"([0-9.]+)", s or "")
    return float(m.group(1)) if m else None
text = Path(out, "kane.ndjson").read_text(encoding="utf-8", errors="replace")
status = None
for line in text.splitlines():
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        continue
    if obj.get("type") == "test_md_done":
        status = obj.get("overall_status")
done = {"suite": suite, "overall_status": status, "balance_before": parse_bal(before), "balance_after": parse_bal(after)}
if done["balance_before"] and done["balance_after"]:
    done["credits"] = round(done["balance_before"] - done["balance_after"], 4)
Path(out, "summary.json").write_text(json.dumps(done, indent=2), encoding="utf-8")
print(json.dumps(done, indent=2))
PY
exit "${KANE_RC:-0}"