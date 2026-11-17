"""CL-1 closed loop. Fixtures are byte-copies of Kane evidence NDJSON."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import kane_loop  # noqa: E402

FIXTURES = REPO / "tests" / "fixtures" / "kane_loop"
NDJSON = REPO / "tests" / "fixtures" / "ndjson"


def test_ndjson_fixtures_match_evidence_bytes():
    provenance = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
    red_meta = next(i for i in provenance["fixtures"] if i["file"] == "attempt1_console.ndjson")
    green_meta = next(i for i in provenance["fixtures"] if i["file"] == "attempt2_console.ndjson")
    for name, meta in (("red.ndjson", red_meta), ("green.ndjson", green_meta)):
        blob = (NDJSON / name).read_bytes()
        packed = zipfile.ZipFile(REPO / meta["evidence"]).read(meta["inner_path"])
        assert blob == packed
        assert hashlib.sha256(blob).hexdigest() == meta["sha256"]


def test_fixtures_match_evidence_bytes():
    provenance = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["fixtures"], "expected real NDJSON fixtures"
    for item in provenance["fixtures"]:
        blob = (FIXTURES / item["file"]).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == item["sha256"]
        packed = zipfile.ZipFile(REPO / item["evidence"]).read(item["inner_path"])
        assert blob == packed
        if blob.strip():
            for line in blob.decode().splitlines():
                if line.strip():
                    assert isinstance(json.loads(line), dict)


def test_failed_actions_are_not_a_pass():
    provenance = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
    actions = next(item for item in provenance["fixtures"] if item["file"] == "attempt1_actions.ndjson")
    events = kane_loop.parse_ndjson((FIXTURES / actions["file"]).read_text(encoding="utf-8"), strict=True)
    assert events
    assert all(event.get("status") == "success" for event in events)
    verdict = kane_loop.evaluate_attempt(
        console_events=[],
        result_status=actions["result_status"],
        pack_status=actions["pack_status"],
    )
    assert actions["pack_status"] == "finalized"
    assert verdict.passed is False
    assert verdict.result_status == "failed"


def test_console_500_is_the_ashby_failure_and_clean_rerun_passes():
    attempts = kane_loop.replay_attempts()
    failed = kane_loop.evaluate_attempt(
        console_events=attempts[0]["console_events"],
        result_status=attempts[0]["result_status"],
        pack_status=attempts[0]["pack_status"],
    )
    passed = kane_loop.evaluate_attempt(
        console_events=attempts[1]["console_events"],
        result_status=attempts[1]["result_status"],
        pack_status=attempts[1]["pack_status"],
    )
    assert failed.passed is False
    assert failed.diagnosis == kane_loop.RESOLVE_FIELDS_500
    assert failed.pack_status == "finalized"
    assert passed.passed is True
    assert passed.diagnosis is None


def test_failure_yaml_loaded_from_pack():
    attempts = kane_loop.replay_attempts()
    assert attempts[0].get("failure_yaml")
    assert attempts[0]["failure_yaml"].get("triage", {}).get("rca", {}).get("category")


def test_evidence_valid_text_does_not_override_a_failed_result():
    verdict = kane_loop.evaluate_attempt(
        console_events=[
            {
                "level": "info",
                "text": "evidence: valid (L1, status finalized)",
                "url": "",
            }
        ],
        result_status="failed",
        pack_status="finalized",
    )
    assert verdict.passed is False


def test_replay_loop_reads_failure_then_passes_on_second_attempt():
    harness = (REPO / "tests" / "kane" / "harness.py").read_text(encoding="utf-8")
    result = kane_loop.run_closed_loop(kane_loop.replay_attempts(), harness)
    assert result.passed is True
    assert result.credits == 0
    assert result.attempts[0]["passed"] is False
    assert result.attempts[0]["diagnosis"] == kane_loop.RESOLVE_FIELDS_500
    assert result.attempts[0]["fixplan"]["items"]
    assert result.attempts[1]["passed"] is True


def test_fixplan_fingerprint_stable():
    harness = "answers[key] = 1\n"
    verdict = kane_loop.Verdict(passed=False, result_status="failed", diagnosis=kane_loop.RESOLVE_FIELDS_500)
    p1 = kane_loop.build_fixplan(verdict, harness)
    p2 = kane_loop.build_fixplan(verdict, harness)
    assert p1 and p2
    assert p1.fingerprint() == p2.fingerprint()
    assert p1.items[0].kind == "harness_patch"


def test_list_index_bug_is_patched_once():
    broken = "answers = resolve()\nfor fld in fields:\n    key = fld.get('id')\n    answers[key] = persona['sponsorship']\n"
    fixed, diff = kane_loop.apply_list_index_fix(broken)
    assert diff["action"] == "patched_list_index"
    assert "def _set_answer" in fixed
    assert "answers[key] =" not in fixed
    again, second = kane_loop.apply_list_index_fix(fixed)
    assert second["action"] == "already_fixed"
    assert again == fixed

    attempts = kane_loop.replay_attempts()
    result = kane_loop.run_closed_loop(attempts, broken)
    assert result.passed is True
    assert result.attempts[0]["fix"] == "patched_list_index"
    assert "answers[key] =" not in result.harness_source


def test_credit_stop_blocks_the_retry():
    attempts = kane_loop.replay_attempts()
    attempts[0]["console_events"] = list(attempts[0]["console_events"]) + [{"credits": 100}]
    result = kane_loop.run_closed_loop(attempts, "answers[key] = 1\n", credit_stop=100)
    assert result.passed is False
    assert result.stopped == "credit_limit"
    assert len(result.attempts) == 1


def test_credit_budget_one_refuses_to_start(capsys):
    code = kane_loop.main(["--replay", "--credit-budget", "1"])
    assert code == 3
    payload = json.loads(capsys.readouterr().out)
    assert payload["stopped"] == "credit_budget_too_low"


def test_command_uses_only_documented_flags(monkeypatch):
    monkeypatch.delenv("LT_USERNAME", raising=False)
    monkeypatch.delenv("LT_ACCESS_KEY", raising=False)
    command = kane_loop.kane_testmd_command(Path("tests/kane/17_persona_visa_ashby_strict_test.md"))
    assert command[1:4] == ["testmd", "run", "tests/kane/17_persona_visa_ashby_strict_test.md"]
    assert command[4:] == ["--agent", "--headless", "--timeout", "180"]
    assert "--local" not in command
    assert "--push" not in command


def test_live_mode_stops_when_kane_cli_is_not_logged_in(capsys, monkeypatch):
    monkeypatch.setattr(kane_loop, "read_whoami", lambda *_a, **_k: "Not logged in")
    code = kane_loop.main(["--live"])
    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["stopped"] == "kane_cli_not_logged_in"
    assert payload["passed"] is False


def test_live_loop_retries_after_the_recorded_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("KANE_CLI", "kane-cli")
    monkeypatch.setattr(kane_loop, "ensure_local_harness", lambda: None)
    outputs = [
        subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout=(FIXTURES / "attempt1_console.ndjson").read_text(encoding="utf-8"),
            stderr="",
        ),
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(FIXTURES / "attempt2_console.ndjson").read_text(encoding="utf-8")
            + json.dumps({"type": "test_md_done", "overall_status": "passed"})
            + "\n",
            stderr="",
        ),
    ]
    calls: list[list[str]] = []

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return outputs.pop(0)

    broken = "answers[key] = persona['sponsorship']\n"
    result = kane_loop.run_live_loop(
        Path("tests/kane/17_persona_visa_ashby_strict_test.md"),
        broken,
        runner,
    )
    assert result.passed is True
    assert len(calls) == 2
    assert calls[0] == calls[1]
    assert result.attempts[0]["fix"] == "patched_list_index"
    assert "def _set_answer" in result.harness_source


def test_localhost_fill_returns_sponsorship_yes():
    kane_loop.clear_seed_bug()
    fill = kane_loop.fill_local()
    assert fill["http_status"] == 200
    assert fill["target"].startswith("http://127.0.0.1")
    answers = fill["answers"]
    assert isinstance(answers, list)
    matched = [item for item in answers if isinstance(item, dict) and item.get("id") == "sponsorship"]
    assert matched and matched[0].get("value") == "Yes"
    encoded = json.dumps(fill)
    assert "greenhouse.io" not in encoded
    assert "lever.co" not in encoded


def test_replay_cli_exits_zero(capsys):
    assert kane_loop.main(["--replay"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is True
    assert payload["credits"] == 0
    assert payload["attempts"][1]["passed"] is True


def test_seed_bug_visa_wrong_answer_plants_no_sponsorship():
    kane_loop.clear_seed_bug()
    kane_loop.clear_agent_policy()
    kane_loop.set_seed_bug("visa_wrong_answer")
    try:
        fill = kane_loop.fill_local(persona="visa_sponsorship")
        assert fill["http_status"] == 200
        answers = fill["answers"]
        matched = [item for item in answers if isinstance(item, dict) and item.get("id") == "sponsorship"]
        assert matched and matched[0].get("value") == "No"
        kane_loop.apply_agent_policy_override("sponsorship", "Yes")
        fill_agent = kane_loop.fill_local(persona="visa_sponsorship")
        matched_agent = [
            item for item in fill_agent["answers"] if isinstance(item, dict) and item.get("id") == "sponsorship"
        ]
        assert matched_agent and matched_agent[0].get("value") == "Yes"
        assert kane_loop.active_seed_bug() == "visa_wrong_answer"
    finally:
        kane_loop.clear_seed_bug()
        kane_loop.clear_agent_policy()


def test_save_evidence_writes_loop_run_tree(tmp_path, monkeypatch):
    monkeypatch.setattr(kane_loop, "LOCAL_RUNS_DIR", tmp_path / "loop_runs")
    run_id = "testrun_save"
    assert kane_loop.main(["--replay", "--save-evidence", "--run-id", run_id]) == 0
    attempt1 = tmp_path / "loop_runs" / run_id / "attempt_1"
    assert (attempt1 / "kane.ndjson").is_file()
    assert (attempt1 / "fixplan.json").is_file()
    assert (tmp_path / "loop_runs" / run_id / "summary.json").is_file()