"""Regression checks for repeatable judge runs and truthful CLI results."""
import argparse
import json
import shutil
from pathlib import Path

import pytest
from ats_verifier import cli
from ats_verifier.official_runs import load_official_runs
from scripts import kane_loop

ROOT = Path(__file__).resolve().parents[1]


def test_local_run_does_not_write_official_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(kane_loop, "LOCAL_RUNS_DIR", tmp_path / "local_runs")
    monkeypatch.setattr(kane_loop, "LOOP_RUNS_DIR", tmp_path / "loop_runs")
    for flags in ([], ["--save-evidence"]):
        assert kane_loop.main(["--replay", *flags]) == 0
    assert not (tmp_path / "loop_runs").exists()
    assert len(list((tmp_path / "local_runs").glob("*/summary.json"))) == 2


def test_official_archive_requires_flags_and_refuses_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(kane_loop, "LOOP_RUNS_DIR", tmp_path / "loop_runs")
    with pytest.raises(SystemExit):
        kane_loop.main(["--replay", "--official", "--run-id", "archived_replay"])
    args = ["--replay", "--save-evidence", "--official", "--run-id", "archived_replay"]
    assert kane_loop.main(args) == 0
    summary = tmp_path / "loop_runs/archived_replay/summary.json"
    before = summary.read_bytes()
    with pytest.raises(SystemExit):
        kane_loop.main(args)
    assert summary.read_bytes() == before


def test_manifest_ignores_unlisted_runs_and_detects_tampering(tmp_path):
    directory = tmp_path / "evidence/loop_runs"
    directory.mkdir(parents=True)
    manifest = json.loads((ROOT / "evidence/loop_runs/MANIFEST.json").read_text())
    for entry in manifest["runs"]:
        destination = directory / entry["run_id"]
        destination.mkdir()
        shutil.copyfile(ROOT / "evidence/loop_runs" / entry["run_id"] / "summary.json", destination / "summary.json")
    (directory / "MANIFEST.json").write_text(json.dumps(manifest))
    unlisted = directory / "unlisted_judge_run"
    unlisted.mkdir()
    (unlisted / "summary.json").write_text('{"mode":"replay"}')
    _, runs = load_official_runs(tmp_path)
    assert len(runs) == 24 and "unlisted_judge_run" not in runs
    first = directory / manifest["runs"][0]["run_id"] / "summary.json"
    first.write_text('{}')
    with pytest.raises(ValueError, match="official summary changed"):
        load_official_runs(tmp_path)


def test_demo_claims_failure_is_not_reported_as_pass(monkeypatch, capsys):
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        return 1 if command == ["scripts/check_claims.py"] else 0
    monkeypatch.setattr(cli, "_run_py", run)
    assert cli.cmd_demo(argparse.Namespace(official=False)) == 1
    output = capsys.readouterr().out
    assert ["scripts/check_claims.py"] in calls
    assert "Claims Gate Check        : FAIL" in output
    assert "DEMO PASSED" not in output


def test_demo_banner_uses_elapsed_time(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
    (tmp_path / "SUBMISSION.json").write_text('{}')
    monkeypatch.setattr(cli, "_run_py", lambda *_a, **_k: 0)
    times = iter([10.0, 12.75])
    monkeypatch.setattr(cli.time, "perf_counter", lambda: next(times))
    assert cli.cmd_demo(argparse.Namespace(official=False)) == 0
    output = capsys.readouterr().out
    assert "PASSED IN 2.75 SECONDS" in output
    assert "< 1.5" not in output


def test_non_tty_doctor_and_policy_diff_have_no_ansi(monkeypatch, capsys):
    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: (_ for _ in ()).throw(OSError("offline")))
    assert cli.cmd_doctor(argparse.Namespace()) == 0
    kane_loop.print_policy_diff({"steps": [{"policy": {"source": "test", "fields": {"sponsorship": "Yes"}}, "action": "policy_override"}]})
    captured = capsys.readouterr()
    assert "System Diagnostic" in captured.out
    assert "Field Overrides" in captured.err
    assert "\x1b" not in captured.out + captured.err


def test_non_official_credit_ledger_stays_local(tmp_path, monkeypatch):
    monkeypatch.setattr(kane_loop, "LOCAL_RUNS_DIR", tmp_path / "local_runs")
    monkeypatch.setattr(kane_loop, "CREDITS_LEDGER", tmp_path / "official.csv")
    kane_loop.append_credits_ledger("judge", "live", 100.0, 99.0, 1.0)
    assert (tmp_path / "local_runs/credits_ledger.csv").is_file()
    assert not (tmp_path / "official.csv").exists()
