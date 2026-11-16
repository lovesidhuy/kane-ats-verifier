#!/usr/bin/env bash
set -euo pipefail

# One-command verification runner for the Kane ATS Verifier hackathon submission
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

pick_python() {
  for cand in "${PYTHON_BIN:-}" python3 /opt/homebrew/opt/python@3.14/bin/python3.14 python3.12 python3.11; do
    [[ -n "$cand" ]] || continue
    if command -v "$cand" >/dev/null 2>&1; then
      if "$cand" -c "import pytest, flask, yaml" 2>/dev/null; then
        echo "$cand"
        return 0
      fi
    fi
  done
  echo "python3"
}

PY_BIN="$(pick_python)"

usage() {
  cat <<'USAGE'
Usage: ./scripts/run_kane_verify.sh <command>

Commands:
  demo     Zero-credit judge demo (unit tests + closed-loop replay artifacts + claims gate)
  doctor   Preflight from a clean clone (no Kane credits required)
  loop     Closed loop: default --replay; pass --live for kane-cli (needs login)
  verify   Unit tests + live Kane harness suites (needs kane-cli login)

Examples:
  ./scripts/run_kane_verify.sh demo
  ./scripts/run_kane_verify.sh loop --replay --save-evidence --run-id judge_demo
  ./scripts/run_kane_verify.sh loop --live --seed-bug visa_wrong_answer --max-attempts 2
USAGE
}

doctor() {
  local ok=0
  echo "== Kane hackathon doctor =="
  command -v "$PY_BIN" >/dev/null || { echo "FAIL: python3 missing"; ok=1; }
  "$PY_BIN" -c "import sys; assert sys.version_info >= (3, 10)" 2>/dev/null || { echo "FAIL: need Python 3.10+"; ok=1; }
  "$PY_BIN" -c "import pytest, flask, yaml" 2>/dev/null || { echo "FAIL: pip install -r requirements.txt"; ok=1; }
  test -f tests/kane/harness.py || { echo "FAIL: harness missing"; ok=1; }
  test -f scripts/kane_loop.py || { echo "FAIL: kane_loop missing"; ok=1; }
  PYTHONPATH=. "$PY_BIN" -c "from ats_verifier.dom_autofill import DOMAutofillEngine" 2>/dev/null \
    || { echo "FAIL: ats_verifier package import failed"; ok=1; }
  if command -v kane-cli >/dev/null; then
    if kane-cli whoami 2>&1 | grep -qiE 'not logged in|not authenticated'; then
      echo "WARN: kane-cli not logged in (replay/demo still work)"
    else
      echo "OK: kane-cli authenticated"
    fi
  else
    echo "WARN: kane-cli not installed (replay/demo still work)"
  fi
  if curl -sf -o /dev/null "http://127.0.0.1:8766/ats/greenhouse" 2>/dev/null; then
    echo "OK: harness already on :8766"
  else
    echo "OK: harness not running (doctor does not start it)"
  fi
  echo "Doctor finished with exit $ok"
  return "$ok"
}

demo() {
  echo "== Judge demo (0 credits, deterministic offline replay) =="
  export FORM_ANSWERS_DISABLE_AI=1
  export KANE_LOOP_DETERMINISTIC=1
  PYTHONPATH=. "$PY_BIN" -m pytest tests/ -q
  PYTHONPATH=. "$PY_BIN" scripts/kane_loop.py --replay --save-evidence --run-id judge_demo
  PYTHONPATH=. "$PY_BIN" scripts/evidence_index.py >/dev/null
  PYTHONPATH=. "$PY_BIN" scripts/check_claims.py >/dev/null
  "$PY_BIN" - <<'PY'
import json
from pathlib import Path
sub = json.loads(Path("SUBMISSION.json").read_text())
summary = json.loads(Path("evidence/loop_runs/judge_demo/summary.json").read_text())
print("")
print("========== JUDGE DEMO SUMMARY (0 credits) ==========")
print(f"Pytest passed: {sub.get('hackathon_pytest_count')}")
print(f"Suites indexed: {sub.get('suites_indexed')} | Loop runs recorded: {sub.get('loop_runs_recorded')} | Sealed packs in repo: {sub.get('sealed_packs_committed')}")
print(f"Trajectories: {sub.get('trajectories_total_claimed')} total, {sub.get('trajectories_sample_committed')} public sample -> evidence/verified_trajectories_sample_50.jsonl")
cr = sub.get("credits") or {}
print(f"Credits (ledger sum): {cr.get('ledger_rows_sum')} | balance delta: {cr.get('ledger_balance_delta')}")
passed = summary.get("passed") or summary.get("overall_status") == "passed"
print(f"Closed-loop replay ({sub.get('demo_run_id')}): {'PASSED' if passed else 'see summary'} -> evidence/loop_runs/judge_demo/summary.json")
print("Claims gate: python3 scripts/check_claims.py")
print("====================================================")
PY
}

run_loop() {
  LIVE=0
  ARGS=()
  for arg in "$@"; do
    if [[ "$arg" == "--live" ]]; then
      LIVE=1
    else
      ARGS+=("$arg")
    fi
  done
  SUITE="tests/kane/17_persona_visa_ashby_strict_test.md"
  for i in "${!ARGS[@]}"; do
    if [[ "${ARGS[$i]}" == "--suite" && -n "${ARGS[$i+1]:-}" ]]; then
      SUITE="${ARGS[$i+1]}"
    fi
  done
  if [[ "$LIVE" -eq 1 ]]; then
    HARNESS_PID=""
    if curl -sf -o /dev/null "http://127.0.0.1:8766/ats/greenhouse" 2>/dev/null; then
      echo "Harness already listening on http://127.0.0.1:8766"
    else
      echo "Starting harness on http://127.0.0.1:8766 for live closed loop..."
      PYTHONPATH=. PORT=8766 "$PY_BIN" tests/kane/harness.py >>/tmp/kane_ats_verifier_harness.log 2>&1 &
      HARNESS_PID=$!
      trap 'kill $HARNESS_PID >/dev/null 2>&1 || true' EXIT
      for _ in 1 2 3 4 5 6 7 8 9 10; do
        if curl -sf -o /dev/null "http://127.0.0.1:8766/ats/greenhouse" 2>/dev/null; then
          break
        fi
        sleep 1
      done
    fi
    exec "$PY_BIN" scripts/kane_loop.py --live --fill --save-evidence --suite "$SUITE" "${ARGS[@]}"
  fi
  echo "CL-1 closed loop (replay, 0 credits)..."
  exec "$PY_BIN" scripts/kane_loop.py --replay --save-evidence "${ARGS[@]}"
}

run_verify() {
  echo "1/4 Running standalone engine & loop unit tests..."
  PYTHONPATH=. "$PY_BIN" -m pytest tests/ -v

  echo "2/4 Starting harness on http://127.0.0.1:8766..."
  PYTHONPATH=. PORT=8766 "$PY_BIN" tests/kane/harness.py >/tmp/kane_ats_verifier_harness.log 2>&1 &
  HARNESS_PID=$!
  trap 'kill $HARNESS_PID >/dev/null 2>&1 || true' EXIT
  sleep 2

  echo "3/4 Kane suites (documented flags: --agent --headless)..."
  kane-cli testmd run tests/kane/01_greenhouse_autofill_test.md --agent --headless --timeout 180
  kane-cli testmd run tests/kane/13_mutated_dom_resilience_test.md --agent --headless --timeout 180
  kane-cli testmd run tests/kane/14_policy_guardrails_test.md --agent --headless --timeout 180

  echo "4/4 Optional: kane-cli evidence validate evidence/*.evidence"
  echo "Done."
}

CMD="${1:-demo}"
case "$CMD" in
  -h|--help|help) usage ;;
  doctor) shift || true; doctor ;;
  demo) shift || true; demo ;;
  loop) shift; run_loop "$@" ;;
  verify) shift || true; run_verify ;;
  *)
    echo "Unknown command: $CMD"
    usage
    exit 2
    ;;
esac
