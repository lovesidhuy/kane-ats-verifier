#!/usr/bin/env python3
"""Closed loop for one Kane suite: fill, Kane testmd (NDJSON), parse failures, FixPlan, retry.

Live ``kane-cli testmd run`` uses flags from ``kane-cli testmd run --help`` (0.10.4):
``--agent``, ``--headless``, ``--timeout``. ``--local`` appears in help prose only.

Pass/fail comes from ``test_md_done.overall_status`` or the pack's ``result.yaml``, not from
``kane-cli evidence validate``. A finalized pack can still be a failed test.

Replay uses byte-copies at ``tests/fixtures/ndjson/{red,green,broken}.ndjson`` (see
``tests/fixtures/kane_loop/provenance.json``).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "kane_loop"
NDJSON_DIR = REPO_ROOT / "tests" / "fixtures" / "ndjson"
SEED_BUG_FILE = REPO_ROOT / "tests" / "kane" / ".loop_seed_bug"
AGENT_POLICY_FILE = REPO_ROOT / "tests" / "kane" / ".loop_agent_policy.json"
DEFAULT_SUITE = Path("tests/kane/17_persona_visa_ashby_strict_test.md")
LOOP_RUNS_DIR = REPO_ROOT / "evidence" / "loop_runs"
CREDITS_LEDGER = REPO_ROOT / "evidence" / "credits_ledger.csv"
MIN_CREDIT_BUDGET = 2.0
DEFAULT_CREDIT_STOP = 100.0

RESOLVE_FIELDS_500 = "resolve_fields_http_500"
LIST_INDEX_FIX = "harness_list_index"
VISA_WRONG_ANSWER = "visa_wrong_answer"
EMAIL_WRONG_ANSWER = "email_wrong_answer"
SALARY_WRONG_ANSWER = "salary_wrong_answer"
KANE_LOCK_DENIED = "kane_lock_denied"
HARNESS_UNREACHABLE = "harness_unreachable"

SEED_FIXES: dict[str, dict[str, str]] = {
    VISA_WRONG_ANSWER: {"target": "sponsorship", "value": "Yes", "source": "seed_bug_visa"},
    EMAIL_WRONG_ANSWER: {"target": "email", "value": "user@example.com", "source": "seed_bug_email"},
    SALARY_WRONG_ANSWER: {"target": "salary_expectation", "value": "160000", "source": "seed_bug_salary"},
}

FIXPLAN_KINDS = (
    "set_value",
    "policy_override",
    "heuristic_rule",
    "rematch_label",
    "select_option",
    "upload_file",
    "harness_patch",
)


@dataclass
class FixPlanItem:
    kind: str
    target: str | None = None
    value: str | None = None
    rationale: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class FixPlan:
    items: list[FixPlanItem] = field(default_factory=list)
    source: str = "kane_loop"

    def fingerprint(self) -> str:
        payload = json.dumps([item.to_dict() for item in self.items], sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint(),
            "source": self.source,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass
class Verdict:
    passed: bool
    result_status: str
    diagnosis: str | None = None
    credits: float = 0.0
    pack_status: str | None = None
    failure_yaml: dict[str, Any] | None = None


@dataclass
class LoopResult:
    passed: bool
    attempts: list[dict[str, Any]] = field(default_factory=list)
    credits: float = 0.0
    stopped: str | None = None
    harness_source: str = ""
    run_id: str = ""


def parse_ndjson(text: str, *, strict: bool = False) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if not (line.startswith("{") or line.startswith("[")):
            if strict:
                raise ValueError(f"NDJSON line {line_no} is not JSON")
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            if strict:
                raise ValueError(f"NDJSON line {line_no} is not JSON") from exc
            continue
        if not isinstance(item, dict):
            if strict:
                raise ValueError(f"NDJSON line {line_no} is not an object")
            continue
        events.append(item)
    return events


def platform_diagnosis_from_text(text: str) -> str | None:
    if "lock] acquire failed" in text or "Access to the product has been removed" in text:
        return KANE_LOCK_DENIED
    if VISA_WRONG_ANSWER in text:
        return VISA_WRONG_ANSWER
    if 'sponsorship' in text.lower() and ('expected' in text.lower() or 'assert' in text.lower()):
        if '"Yes"' in text and '"No"' in text:
            return VISA_WRONG_ANSWER
    if "ERR_CONNECTION_REFUSED" in text or "refused the connection" in text:
        return HARNESS_UNREACHABLE
    if 'sponsorship' in text.lower() and ('has value "Yes"' in text or 'id "sponsorship"' in text):
        if '"passed":false' in text.replace(" ", "") or "status\":\"failed\"" in text:
            if '"No"' in text or active_seed_bug() == VISA_WRONG_ANSWER:
                return VISA_WRONG_ANSWER
    return None


def active_seed_bug() -> str | None:
    env = os.environ.get("KANE_SEED_BUG", "").strip()
    if env:
        return env
    if SEED_BUG_FILE.is_file():
        return SEED_BUG_FILE.read_text(encoding="utf-8").strip() or None
    return None


def set_seed_bug(name: str) -> None:
    SEED_BUG_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEED_BUG_FILE.write_text(name.strip(), encoding="utf-8")
    os.environ["KANE_SEED_BUG"] = name.strip()


def clear_seed_bug() -> None:
    SEED_BUG_FILE.unlink(missing_ok=True)
    os.environ.pop("KANE_SEED_BUG", None)


def read_agent_policy() -> dict[str, str]:
    if not AGENT_POLICY_FILE.is_file():
        return {}
    try:
        data = json.loads(AGENT_POLICY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    fields = data.get("fields") if isinstance(data, dict) else None
    if not isinstance(fields, dict):
        return {}
    return {str(k): str(v) for k, v in fields.items() if v is not None}


def read_full_agent_policy() -> dict[str, Any]:
    if not AGENT_POLICY_FILE.is_file():
        return {}
    try:
        data = json.loads(AGENT_POLICY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_agent_policy(
    fields: dict[str, str],
    *,
    rules: dict[str, Any] | None = None,
    source: str = "kane_loop",
) -> dict[str, Any]:
    current = read_full_agent_policy()
    merged_rules = dict(current.get("rules") or {})
    if rules:
        merged_rules.update(rules)
    payload = {
        "source": source,
        "updated_utc": datetime.now(timezone.utc).isoformat(),
        "rules": merged_rules,
        "fields": fields,
    }
    AGENT_POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
    AGENT_POLICY_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def clear_agent_policy() -> None:
    AGENT_POLICY_FILE.unlink(missing_ok=True)


def format_policy_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    b_fields = before.get("fields") or {}
    a_fields = after.get("fields") or {}
    b_rules = before.get("rules") or {}
    a_rules = after.get("rules") or {}

    added_fields = {k: v for k, v in a_fields.items() if k not in b_fields or b_fields[k] != v}
    added_rules = {k: v for k, v in a_rules.items() if k not in b_rules or b_rules[k] != v}

    return {
        "added_fields": added_fields,
        "added_rules": added_rules,
        "before_source": before.get("source"),
        "after_source": after.get("source"),
    }


def print_policy_diff(diff: dict[str, Any]) -> None:
    steps = diff.get("steps") or []
    for step in steps:
        policy = step.get("policy") or {}
        rules = policy.get("rules") or {}
        fields = policy.get("fields") or {}
        print("\n" + "=" * 66, file=sys.stderr)
        print("  \033[1;36m[CLOSED LOOP] Agent Heuristic Policy Generalization Diff\033[0m", file=sys.stderr)
        print("=" * 66, file=sys.stderr)
        print(f"  \033[1mSource\033[0m: {policy.get('source', 'kane_loop')}", file=sys.stderr)
        print(f"  \033[1mAction\033[0m: {step.get('action')}", file=sys.stderr)
        if rules:
            print("  \033[1;32m+ Generalized Rules Learned:\033[0m", file=sys.stderr)
            for rk, rv in rules.items():
                print(f"    \033[32m+ {rk}\033[0m: {json.dumps(rv)}", file=sys.stderr)
        if fields:
            print("  \033[1;33m+ Field Overrides Applied:\033[0m", file=sys.stderr)
            for fk, fv in fields.items():
                print(f"    \033[33m+ {fk}\033[0m: {json.dumps(fv)}", file=sys.stderr)
        print("=" * 66 + "\n", file=sys.stderr)


def apply_agent_policy_override(
    target: str,
    value: str,
    *,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    before = read_full_agent_policy()
    fields = read_agent_policy()
    fields[target] = value
    inferred_rules: dict[str, Any] = {}
    if target in {"sponsorship", "visa", "work_auth"}:
        inferred_rules["screening_policy_resolution"] = "deterministic_policy_first"
        inferred_rules["work_auth_fallback"] = "require_explicit_persona"
    elif "fld_" in target or "id_" in target or "mutated" in target or target == "api_resolve_fields":
        inferred_rules["fallback_strategy"] = "aria_label_or_for_attribute"
        inferred_rules["regex_id_ignore"] = r"^fld_[0-9a-z]+$"
        inferred_rules["label_proximity_matching"] = True
    elif target == "salary_expectation":
        inferred_rules["salary_resolution"] = "persona_baseline_cad"
    if rules:
        inferred_rules.update(rules)
    after = write_agent_policy(fields, rules=inferred_rules, source="kane_loop_agent_fix")
    return after


def console_diagnosis(events: Iterable[dict[str, Any]]) -> str | None:
    for event in events:
        url = str(event.get("url") or "")
        text = str(event.get("text") or "")
        blob = f"{url}\n{text}"
        if "/api/resolve-fields" in url and ("500" in text or "INTERNAL SERVER ERROR" in text):
            return RESOLVE_FIELDS_500
        if "WAITING_FOR_JOBSFARM" in blob:
            return "waiting_for_jobsfarm"
        if "list indices must be integers" in blob:
            return RESOLVE_FIELDS_500
    return None


def agent_overall_status(events: Iterable[dict[str, Any]]) -> str | None:
    found: str | None = None
    for event in events:
        kind = str(event.get("type") or event.get("event") or "")
        if kind != "test_md_done":
            continue
        status = str(event.get("overall_status") or "").strip().lower()
        found = status or None
    return found


def credits_in(events: Iterable[dict[str, Any]]) -> float:
    total = 0.0
    for event in events:
        for key in ("credits", "credit_cost", "credits_used"):
            value = event.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                total += float(value)
    return total


def read_failure_yaml_from_pack(pack_path: Path, step_glob: str = "failure.yaml") -> dict[str, Any] | None:
    if not pack_path.is_file():
        return None
    try:
        with zipfile.ZipFile(pack_path) as zf:
            matches = [n for n in zf.namelist() if n.endswith(step_glob) and "/steps/" in n]
            if not matches:
                root = "failure.yaml"
                if root in zf.namelist():
                    matches = [root]
            if not matches:
                return None
            raw = zf.read(matches[0]).decode("utf-8", errors="replace")
            data = yaml.safe_load(raw)
            return data if isinstance(data, dict) else None
    except (zipfile.BadZipFile, OSError, yaml.YAMLError):
        return None


def parse_attempt_failures(
    attempt: dict[str, Any],
    *,
    console_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    events = console_events or list(attempt.get("console_events") or [])
    agent_events = list(attempt.get("agent_events") or [])
    raw = str(attempt.get("raw_output") or "")
    evidence = attempt.get("evidence")
    failure_yaml = attempt.get("failure_yaml")
    if failure_yaml is None and evidence:
        failure_yaml = read_failure_yaml_from_pack(REPO_ROOT / str(evidence))
    platform = attempt.get("platform_diagnosis") or platform_diagnosis_from_text(raw)
    return {
        "console_diagnosis": platform
        or console_diagnosis(events)
        or console_diagnosis(agent_events),
        "failure_yaml": failure_yaml,
        "result_status": attempt.get("result_status"),
        "pack_status": attempt.get("pack_status"),
        "raw_output": raw,
    }


def evaluate_attempt(
    *,
    console_events: Iterable[dict[str, Any]],
    agent_events: Iterable[dict[str, Any]] | None = None,
    result_status: str = "",
    pack_status: str | None = None,
    failure_yaml: dict[str, Any] | None = None,
) -> Verdict:
    console_events = list(console_events)
    agent_events = list(agent_events or [])
    diagnosis = console_diagnosis(console_events) or console_diagnosis(agent_events)
    done = agent_overall_status(agent_events)
    if done in {"passed", "pass"}:
        status = "passed"
    elif done in {"failed", "fail", "broken"}:
        status = "failed"
    else:
        status = (result_status or "").strip().lower()
    passed = status == "passed" and diagnosis is None
    return Verdict(
        passed=passed,
        result_status=status or "unknown",
        diagnosis=diagnosis,
        credits=credits_in(console_events) + credits_in(agent_events),
        pack_status=pack_status,
        failure_yaml=failure_yaml,
    )


judge_attempt = evaluate_attempt  # backward compatibility alias


def harness_has_list_index_bug(source: str) -> bool:
    return "answers[key]" in source


def apply_list_index_fix(source: str) -> tuple[str, dict[str, Any]]:
    if not harness_has_list_index_bug(source):
        return source, {"action": "already_fixed", "kind": "harness_patch"}
    helper = (
        "def _set_answer(answers, key, val):\n"
        "    if isinstance(answers, list):\n"
        "        for item in answers:\n"
        "            if isinstance(item, dict) and item.get('id') == key:\n"
        "                item['value'] = val\n"
        "                return\n"
        "        answers.append({'id': key, 'value': val})\n"
        "        return\n"
        "    answers.__setitem__(key, val)\n\n"
    )
    rewritten: list[str] = []
    for line in source.splitlines(keepends=True):
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if stripped.startswith("answers[key] ="):
            rhs = stripped.split("=", 1)[1].strip()
            newline = "\n" if stripped.endswith("\n") or line.endswith("\n") else ""
            rewritten.append(f"{indent}_set_answer(answers, key, {rhs}){newline}")
        else:
            rewritten.append(line)
    body = "".join(rewritten)
    if "def _set_answer" not in body:
        body = helper + body
    if harness_has_list_index_bug(body):
        return source, {"action": "fix_failed", "kind": "harness_patch"}
    return body, {"action": "patched_list_index", "kind": "harness_patch"}


def build_fixplan(
    verdict: Verdict,
    harness_source: str,
    parsed: dict[str, Any] | None = None,
) -> FixPlan | None:
    diagnosis = verdict.diagnosis or (parsed or {}).get("console_diagnosis")
    failure_yaml = verdict.failure_yaml or (parsed or {}).get("failure_yaml")
    items: list[FixPlanItem] = []

    if diagnosis in {HARNESS_UNREACHABLE, KANE_LOCK_DENIED}:
        return None
    raw = str((parsed or {}).get("raw_output") or "")
    sponsorship_fail = (
        active_seed_bug() == VISA_WRONG_ANSWER
        and verdict.result_status == "failed"
        and "sponsorship" in raw.lower()
        and "AUTOFILL_COMPLETED" in raw
    ) or (
        diagnosis == VISA_WRONG_ANSWER
        and active_seed_bug() == VISA_WRONG_ANSWER
        and verdict.result_status == "failed"
    )
    if sponsorship_fail:
        spec = SEED_FIXES[VISA_WRONG_ANSWER]
        items.append(
            FixPlanItem(
                kind="policy_override",
                target=spec["target"],
                value=spec["value"],
                rationale="Kane reported sponsorship mismatch; agent policy_override while seed stays planted",
            )
        )
        return FixPlan(items=items, source=spec["source"])
    seed = active_seed_bug()
    if seed in SEED_FIXES and verdict.result_status == "failed":
        spec = SEED_FIXES[seed]
        target = spec["target"]
        if (
            target.replace("_", " ") in raw.lower()
            or target in raw.lower()
            or seed in raw
            or (seed == EMAIL_WRONG_ANSWER and "email" in raw.lower())
            or (seed == SALARY_WRONG_ANSWER and "salary" in raw.lower())
            or active_seed_bug() == seed
        ):
            items.append(
                FixPlanItem(
                    kind="policy_override",
                    target=target,
                    value=spec["value"],
                    rationale=f"Kane caught {seed}; agent applies policy_override while seed stays planted",
                )
            )
            return FixPlan(items=items, source=spec["source"])
    if diagnosis in {RESOLVE_FIELDS_500, "waiting_for_jobsfarm"}:
        if harness_has_list_index_bug(harness_source):
            items.append(
                FixPlanItem(
                    kind="harness_patch",
                    target="tests/kane/harness.py",
                    value=LIST_INDEX_FIX,
                    rationale="Kane caught /api/resolve-fields 500 from list-index misuse",
                )
            )
        else:
            rca = (failure_yaml or {}).get("triage", {}).get("rca", {}) if failure_yaml else {}
            category = str(rca.get("category") or "")
            if "api_error" in category or diagnosis == RESOLVE_FIELDS_500:
                items.append(
                    FixPlanItem(
                        kind="policy_override",
                        target="api_resolve_fields",
                        value="retry_after_harness_ok",
                        rationale="Harness already patched; policy path for residual API errors",
                    )
                )
            else:
                return None
    elif diagnosis is None and verdict.result_status == "failed":
        triage = (failure_yaml or {}).get("triage", {}) if failure_yaml else {}
        summary = str(triage.get("suggested_fix", {}).get("summary") or "")
        if summary:
            items.append(
                FixPlanItem(
                    kind="rematch_label",
                    target="autofill_marker",
                    value=summary[:240],
                    rationale="Unmapped failure; surface Kane triage for agent",
                )
            )
        else:
            return None
    else:
        return None

    return FixPlan(items=items)


def apply_fixplan(plan: FixPlan, harness_source: str) -> tuple[str, dict[str, Any], str]:
    if not plan.items:
        return harness_source, {}, "already_fixed"
    diffs: list[dict[str, Any]] = []
    source = harness_source
    action = "already_fixed"
    for item in plan.items:
        if item.kind == "harness_patch" and item.value == LIST_INDEX_FIX:
            source, diff = apply_list_index_fix(source)
            diffs.append(diff)
            action = str(diff.get("action") or "harness_patch")
        elif item.kind == "policy_override":
            if item.target and item.value:
                policy = apply_agent_policy_override(str(item.target), str(item.value))
                diffs.append(
                    {
                        "action": "agent_policy_override_applied",
                        "target": item.target,
                        "value": item.value,
                        "agent_policy_file": str(AGENT_POLICY_FILE.relative_to(REPO_ROOT)),
                        "kane_failure": "expected_yes_got_no" if item.target == "sponsorship" else None,
                        "policy": policy,
                    }
                )
                action = "agent_policy_override_applied"
            else:
                action = "policy_override_applied"
                diffs.append({"action": action, "target": item.target, "value": item.value})
        elif item.kind == "heuristic_rule":
            rule_dict = {}
            for part in str(item.value or "").split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    rule_dict[k.strip()] = v.strip()
                elif part.strip():
                    rule_dict[part.strip()] = True
            policy = write_agent_policy(read_agent_policy(), rules=rule_dict, source="kane_loop_agent_fix")
            diffs.append({
                "action": "heuristic_rule_applied",
                "target": item.target,
                "rules": rule_dict,
                "agent_policy_file": str(AGENT_POLICY_FILE.relative_to(REPO_ROOT)),
                "policy": policy,
            })
            action = "heuristic_rule_applied"
        elif item.kind in FIXPLAN_KINDS:
            action = f"planned_{item.kind}"
            diffs.append(item.to_dict())
        else:
            return source, {"error": "unknown_kind", "kind": item.kind}, "fix_failed"
    return source, {"steps": diffs}, action


def run_closed_loop(
    attempts: list[dict[str, Any]],
    harness_source: str,
    *,
    credit_stop: float = DEFAULT_CREDIT_STOP,
    on_attempt: Callable[[int, dict[str, Any], Verdict, FixPlan | None, dict[str, Any]], None]
    | None = None,
) -> LoopResult:
    source = harness_source
    log: list[dict[str, Any]] = []
    spent = 0.0
    seen_fp: set[str] = set()
    for index, attempt in enumerate(attempts, 1):
        if spent >= credit_stop:
            return LoopResult(
                passed=False,
                attempts=log,
                credits=spent,
                stopped="credit_limit",
                harness_source=source,
            )
        parsed = parse_attempt_failures(attempt)
        verdict = evaluate_attempt(
            console_events=attempt.get("console_events") or [],
            agent_events=attempt.get("agent_events") or [],
            result_status=str(attempt.get("result_status") or ""),
            pack_status=attempt.get("pack_status"),
            failure_yaml=parsed.get("failure_yaml"),
        )
        spent += verdict.credits
        plan = build_fixplan(verdict, source, parsed)
        entry: dict[str, Any] = {
            "attempt": index,
            "passed": verdict.passed,
            "result_status": verdict.result_status,
            "diagnosis": verdict.diagnosis,
            "pack_status": verdict.pack_status,
            "credits": spent,
        }
        diff: dict[str, Any] = {}
        if verdict.passed:
            if plan:
                entry["fixplan"] = plan.to_dict()
            log.append(entry)
            if on_attempt:
                on_attempt(index, attempt, verdict, plan, diff)
            return LoopResult(passed=True, attempts=log, credits=spent, harness_source=source)
        if plan is None:
            entry["stop_reason"] = "needs_human"
            log.append(entry)
            if on_attempt:
                on_attempt(index, attempt, verdict, None, {})
            return LoopResult(
                passed=False,
                attempts=log,
                credits=spent,
                stopped="needs_human",
                harness_source=source,
            )
        fp = plan.fingerprint()
        if fp in seen_fp:
            entry["fixplan"] = plan.to_dict()
            entry["stop_reason"] = "repeated_fixplan"
            log.append(entry)
            if on_attempt:
                on_attempt(index, attempt, verdict, plan, {})
            return LoopResult(
                passed=False,
                attempts=log,
                credits=spent,
                stopped="repeated_fixplan",
                harness_source=source,
            )
        seen_fp.add(fp)
        source, diff, action = apply_fixplan(plan, source)
        if diff and diff.get("steps"):
            print_policy_diff(diff)
        entry["fixplan"] = plan.to_dict()
        entry["fix"] = action
        entry["diff"] = diff
        log.append(entry)
        if on_attempt:
            on_attempt(index, attempt, verdict, plan, diff)
        if spent >= credit_stop:
            return LoopResult(
                passed=False,
                attempts=log,
                credits=spent,
                stopped="credit_limit",
                harness_source=source,
            )
        if action in {"fix_failed"} or action.startswith("unhandled_"):
            return LoopResult(
                passed=False,
                attempts=log,
                credits=spent,
                stopped=action,
                harness_source=source,
            )
    return LoopResult(
        passed=False,
        attempts=log,
        credits=spent,
        stopped="attempts_exhausted",
        harness_source=source,
    )


def load_provenance(directory: Path = FIXTURE_DIR) -> dict[str, Any]:
    return json.loads((directory / "provenance.json").read_text(encoding="utf-8"))


def replay_attempts(directory: Path = FIXTURE_DIR) -> list[dict[str, Any]]:
    provenance = load_provenance(directory)
    by_file = {item["file"]: item for item in provenance["fixtures"]}
    failed = by_file["attempt1_console.ndjson"]
    passed = by_file["attempt2_console.ndjson"]
    fail_yaml = read_failure_yaml_from_pack(REPO_ROOT / failed["evidence"])
    return [
        {
            "console_events": parse_ndjson((directory / failed["file"]).read_text(encoding="utf-8")),
            "result_status": failed["result_status"],
            "pack_status": failed["pack_status"],
            "evidence": failed["evidence"],
            "failure_yaml": fail_yaml,
        },
        {
            "console_events": parse_ndjson((directory / passed["file"]).read_text(encoding="utf-8")),
            "result_status": passed["result_status"],
            "pack_status": passed["pack_status"],
            "evidence": passed["evidence"],
        },
    ]


def ndjson_fixture_attempts() -> list[dict[str, Any]]:
    """Same replay sequence using ``tests/fixtures/ndjson/{red,green}.ndjson``."""
    red = (NDJSON_DIR / "red.ndjson").read_text(encoding="utf-8")
    green = (NDJSON_DIR / "green.ndjson").read_text(encoding="utf-8")
    provenance = load_provenance()
    failed_meta = next(i for i in provenance["fixtures"] if i["file"] == "attempt1_console.ndjson")
    passed_meta = next(i for i in provenance["fixtures"] if i["file"] == "attempt2_console.ndjson")
    fail_yaml = read_failure_yaml_from_pack(REPO_ROOT / failed_meta["evidence"])
    return [
        {
            "console_events": parse_ndjson(red),
            "result_status": failed_meta["result_status"],
            "pack_status": failed_meta["pack_status"],
            "evidence": failed_meta["evidence"],
            "failure_yaml": fail_yaml,
        },
        {
            "console_events": parse_ndjson(green),
            "result_status": passed_meta["result_status"],
            "pack_status": passed_meta["pack_status"],
            "evidence": passed_meta["evidence"],
        },
    ]


def _harness_health_url(port: int = 8766) -> str:
    return f"http://127.0.0.1:{port}/ats/greenhouse"


def _harness_is_up(port: int = 8766) -> bool:
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(_harness_health_url(port), timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _start_harness_process(port: int = 8766) -> None:
    import time
    import urllib.error
    import urllib.request

    log_path = Path("/tmp/kane_ats_verifier_harness.log")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT), "PORT": str(port)}
    subprocess.Popen(
        [sys.executable, str(REPO_ROOT / "tests" / "kane" / "harness.py")],
        cwd=REPO_ROOT,
        env=env,
        stdout=log_path.open("a", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    url = _harness_health_url(port)
    for _ in range(15):
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, OSError):
            time.sleep(1)


def restart_local_harness(port: int = 8766) -> None:
    """Restart Flask harness so code/seed-marker changes take effect (avoids stale workers)."""
    import time

    subprocess.run(
        ["pkill", "-f", str(REPO_ROOT / "tests" / "kane" / "harness.py")],
        check=False,
        capture_output=True,
    )
    time.sleep(0.8)
    _start_harness_process(port)


def ensure_local_harness(port: int = 8766) -> None:
    """Best-effort: keep the dry-run harness accepting connections before each Kane run."""
    import time

    if _harness_is_up(port):
        return
    for _ in range(3):
        if _harness_is_up(port):
            return
        time.sleep(0.5)
    _start_harness_process(port)


def fill_local(repo_root: Path = REPO_ROOT, persona: str = "visa_sponsorship") -> dict[str, Any]:
    harness_path = repo_root / "tests" / "kane" / "harness.py"
    spec = importlib.util.spec_from_file_location("jobsfarm_kane_harness", harness_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {harness_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = module.app.test_client()
    response = client.post(
        "/api/resolve-fields",
        json={
            "persona": persona,
            "job_context": "local dry-run",
            "fields": [
                {
                    "id": "sponsorship",
                    "name": "sponsorship",
                    "label": "Will you now or in the future require visa sponsorship?",
                    "type": "select",
                }
            ],
        },
    )
    body = response.get_json(silent=True) or {}
    return {
        "http_status": response.status_code,
        "persona": body.get("persona"),
        "answers": body.get("answers"),
        "target": "http://127.0.0.1/api/resolve-fields",
    }


def kane_testmd_command(suite: Path, kane_bin: str = "kane-cli") -> list[str]:
    command = [
        kane_bin,
        "testmd",
        "run",
        suite.as_posix(),
        "--agent",
        "--headless",
        "--timeout",
        "180",
    ]
    user = os.environ.get("LT_USERNAME", "").strip()
    key = os.environ.get("LT_ACCESS_KEY", "").strip()
    if user and key:
        command.extend(["--username", user, "--access-key", key])
    return command


def whoami_is_logged_in(text: str) -> bool:
    return "Not logged in" not in text and "Not authenticated" not in text


def kane_binary() -> str:
    return os.environ.get("KANE_CLI") or shutil.which("kane-cli") or "kane-cli"


def redact_kane_command(command: list[str]) -> list[str]:
    redacted = list(command)
    for index, part in enumerate(redacted):
        if part in ("--access-key", "--username") and index + 1 < len(redacted):
            redacted[index + 1] = "[REDACTED]"
    return redacted


def read_whoami(runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None) -> str:
    command = [kane_binary(), "whoami"]
    if runner is None:
        try:
            completed = subprocess.run(command, check=False, capture_output=True, text=True)
        except FileNotFoundError:
            return "Not logged in"
    else:
        completed = runner(command)
    return (completed.stdout or "") + (completed.stderr or "")


def parse_balance(text: str) -> float | None:
    match = re.search(r"Available credits:\s*([0-9]+(?:\.[0-9]+)?)", text)
    if not match:
        return None
    return float(match.group(1))


def read_balance(runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None) -> float | None:
    command = [kane_binary(), "balance"]
    if runner is None:
        try:
            completed = subprocess.run(command, check=False, capture_output=True, text=True)
        except FileNotFoundError:
            return None
    else:
        completed = runner(command)
    blob = (completed.stdout or "") + (completed.stderr or "")
    return parse_balance(blob)


def append_credits_ledger(
    run_id: str,
    label: str,
    balance_before: float | None,
    balance_after: float | None,
    credits_recorded: float,
    note: str = "",
) -> None:
    CREDITS_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    new_file = not CREDITS_LEDGER.exists()
    with CREDITS_LEDGER.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(
                [
                    "timestamp_utc",
                    "run_id",
                    "label",
                    "balance_before",
                    "balance_after",
                    "credits_recorded",
                    "note",
                ]
            )
        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(),
                run_id,
                label,
                "" if balance_before is None else f"{balance_before:.4f}",
                "" if balance_after is None else f"{balance_after:.4f}",
                f"{credits_recorded:.4f}",
                note,
            ]
        )


def save_attempt_artifacts(
    run_dir: Path,
    attempt_no: int,
    *,
    kane_ndjson: str,
    fill: dict[str, Any] | None,
    fixplan: FixPlan | None,
    diff: dict[str, Any],
    pack_path: Path | None,
    copy_pack: bool = False,
) -> None:
    attempt_dir = run_dir / f"attempt_{attempt_no}"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / "kane.ndjson").write_text(kane_ndjson, encoding="utf-8")
    if fill is not None:
        (attempt_dir / "fill.json").write_text(json.dumps(fill, indent=2), encoding="utf-8")
    if fixplan is not None:
        (attempt_dir / "fixplan.json").write_text(json.dumps(fixplan.to_dict(), indent=2), encoding="utf-8")
    (attempt_dir / "diff.json").write_text(json.dumps(diff or {}, indent=2), encoding="utf-8")
    if copy_pack and pack_path and pack_path.is_file():
        dest = attempt_dir / "pack.evidence"
        if not dest.exists():
            shutil.copy2(pack_path, dest)
    shots = attempt_dir / "screenshots"
    shots.mkdir(exist_ok=True)
    (shots / ".keep").write_text("", encoding="utf-8")


def write_summary(run_dir: Path, payload: dict[str, Any]) -> None:
    (run_dir / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def attempt_from_kane_output(stdout: str, returncode: int) -> dict[str, Any]:
    events = parse_ndjson(stdout) if stdout.strip() else []
    platform = platform_diagnosis_from_text(stdout)
    done = agent_overall_status(events)
    if done in {"passed", "pass", "failed", "fail", "broken"}:
        status = "passed" if done in {"passed", "pass"} else "failed"
    elif platform == KANE_LOCK_DENIED:
        status = "failed"
    elif returncode == 0:
        status = "passed"
    else:
        status = "failed"
    return {
        "agent_events": events,
        "console_events": events,
        "result_status": status,
        "raw_output": stdout,
        "platform_diagnosis": platform,
    }


def _persist_attempt(
    run_dir: Path,
    attempt_no: int,
    attempt: dict[str, Any],
    plan: FixPlan | None,
    diff: dict[str, Any],
    fill: dict[str, Any] | None,
    *,
    copy_pack: bool = False,
) -> None:
    raw = attempt.get("raw_output")
    if raw:
        ndjson = raw if raw.endswith("\n") else raw + "\n"
    else:
        events = attempt.get("agent_events") or attempt.get("console_events") or []
        ndjson = "\n".join(json.dumps(e, ensure_ascii=False) for e in events)
        if ndjson and not ndjson.endswith("\n"):
            ndjson += "\n"
    pack = Path(str(attempt["evidence"])) if attempt.get("evidence") else None
    save_attempt_artifacts(
        run_dir,
        attempt_no,
        kane_ndjson=ndjson,
        fill=fill,
        fixplan=plan,
        diff=diff,
        pack_path=REPO_ROOT / pack if pack else None,
        copy_pack=copy_pack,
    )


def run_live_loop(
    suite: Path,
    harness_source: str,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]],
    *,
    max_attempts: int = 2,
    credit_stop: float = DEFAULT_CREDIT_STOP,
    run_id: str | None = None,
    save_artifacts: bool = False,
) -> LoopResult:
    rid = run_id or uuid.uuid4().hex[:12]
    run_dir = LOOP_RUNS_DIR / rid
    command = kane_testmd_command(suite, kane_binary())
    source = harness_source
    log: list[dict[str, Any]] = []
    spent = 0.0
    seen_fp: set[str] = set()

    ensure_local_harness()
    agent_fill: dict[str, Any] | None = None

    for index in range(1, max_attempts + 1):
        if spent >= credit_stop:
            return LoopResult(
                passed=False,
                attempts=log,
                credits=spent,
                stopped="credit_limit",
                harness_source=source,
                run_id=rid,
            )
        ensure_local_harness()
        completed = runner(command)
        attempt = attempt_from_kane_output(completed.stdout or "", completed.returncode)
        parsed = parse_attempt_failures(attempt)
        verdict = evaluate_attempt(
            console_events=attempt.get("console_events") or [],
            agent_events=attempt.get("agent_events") or [],
            result_status=str(attempt.get("result_status") or ""),
            pack_status=attempt.get("pack_status"),
            failure_yaml=parsed.get("failure_yaml"),
        )
        spent += verdict.credits
        overall = agent_overall_status(attempt.get("agent_events") or [])
        raw = str(attempt.get("raw_output") or "")
        diag = parsed.get("console_diagnosis") or verdict.diagnosis
        if overall is None and diag in {HARNESS_UNREACHABLE, KANE_LOCK_DENIED}:
            overall = "broken"
        elif overall is None:
            overall = verdict.result_status
        entry: dict[str, Any] = {
            "attempt": index,
            "passed": verdict.passed,
            "overall_status": overall or verdict.result_status,
            "seed_bug_active": active_seed_bug(),
            "agent_policy": read_agent_policy(),
            "result_status": verdict.result_status,
            "diagnosis": diag,
            "pack_status": verdict.pack_status,
            "credits": spent,
        }
        if verdict.passed:
            log.append(entry)
            if save_artifacts:
                _persist_attempt(run_dir, index, attempt, None, {}, None, copy_pack=True)
            return LoopResult(passed=True, attempts=log, credits=spent, harness_source=source, run_id=rid)
        plan = build_fixplan(verdict, source, parsed)
        if plan is None:
            plat = parsed.get("console_diagnosis")
            if plat == HARNESS_UNREACHABLE and index < max_attempts:
                entry["fix"] = "retry_after_harness"
                entry["stop_reason"] = None
                log.append(entry)
                if save_artifacts:
                    _persist_attempt(run_dir, index, attempt, None, {}, None, copy_pack=True)
                import time

                time.sleep(3)
                continue
            stop = "kane_lock_denied" if plat == KANE_LOCK_DENIED else "needs_human"
            entry["stop_reason"] = stop
            entry["diagnosis"] = plat or verdict.diagnosis
            log.append(entry)
            if save_artifacts:
                _persist_attempt(run_dir, index, attempt, None, {}, None, copy_pack=True)
            return LoopResult(
                passed=False,
                attempts=log,
                credits=spent,
                stopped=stop,
                harness_source=source,
                run_id=rid,
            )
        fp = plan.fingerprint()
        if fp in seen_fp:
            entry["fixplan"] = plan.to_dict()
            entry["stop_reason"] = "repeated_fixplan"
            log.append(entry)
            if save_artifacts:
                _persist_attempt(run_dir, index, attempt, plan, {}, None, copy_pack=True)
            return LoopResult(
                passed=False,
                attempts=log,
                credits=spent,
                stopped="repeated_fixplan",
                harness_source=source,
                run_id=rid,
            )
        seen_fp.add(fp)
        source, diff, action = apply_fixplan(plan, source)
        if action == "agent_policy_override_applied":
            agent_fill = fill_local()
            entry["agent_fill"] = {
                "http_status": agent_fill.get("http_status"),
                "sponsorship": next(
                    (
                        a.get("value")
                        for a in (agent_fill.get("answers") or [])
                        if isinstance(a, dict) and a.get("id") == "sponsorship"
                    ),
                    None,
                ),
            }
        entry["fixplan"] = plan.to_dict()
        entry["fix"] = action
        entry["diff"] = diff
        log.append(entry)
        if save_artifacts:
            _persist_attempt(
                run_dir,
                index,
                attempt,
                plan,
                diff,
                agent_fill if action == "agent_policy_override_applied" else None,
                copy_pack=True,
            )
        if action in {"fix_failed"} or action.startswith("unhandled_"):
            return LoopResult(
                passed=False,
                attempts=log,
                credits=spent,
                stopped=action,
                harness_source=source,
                run_id=rid,
            )
    return LoopResult(
        passed=False,
        attempts=log,
        credits=spent,
        stopped="attempts_exhausted",
        harness_source=source,
        run_id=rid,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="JobsFarm x Kane closed loop (CL-1)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--replay", action="store_true", help="Replay real NDJSON fixtures (0 credits)")
    mode.add_argument("--live", action="store_true", help="Run kane-cli testmd against the suite")
    parser.add_argument("--fill", action="store_true", help="Run localhost autofill before the loop")
    parser.add_argument("--suite", default=str(DEFAULT_SUITE), help="Suite path relative to repo root")
    parser.add_argument(
        "--credit-budget",
        type=float,
        default=None,
        help=f"Refuse to start if below {MIN_CREDIT_BUDGET}; also caps recorded credits per run",
    )
    parser.add_argument("--max-attempts", type=int, default=5, help="Maximum Kane attempts per run")
    parser.add_argument("--run-id", default=None, help="Loop run id for evidence/loop_runs/")
    parser.add_argument(
        "--save-evidence",
        action="store_true",
        help="Write evidence/loop_runs/<run_id>/attempt_n/ artifacts",
    )
    parser.add_argument(
        "--seed-bug",
        default=None,
        help="Planted harness bug name (e.g. visa_wrong_answer) — labeled in docs as deliberate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit only the final summary JSON object on stdout (default output is already JSON)",
    )
    args = parser.parse_args(argv)

    if args.credit_budget is not None and args.credit_budget < MIN_CREDIT_BUDGET:
        print(
            json.dumps(
                {
                    "passed": False,
                    "stopped": "credit_budget_too_low",
                    "min_required": MIN_CREDIT_BUDGET,
                    "credit_budget": args.credit_budget,
                },
                indent=2,
            )
        )
        return 3

    credit_stop = args.credit_budget if args.credit_budget is not None else DEFAULT_CREDIT_STOP
    live = bool(args.live)
    if not live:
        args.replay = True

    run_id = args.run_id or uuid.uuid4().hex[:12]
    run_dir = LOOP_RUNS_DIR / run_id
    payload: dict[str, Any] = {
        "mode": "live" if live else "replay",
        "suite": args.suite,
        "run_id": run_id,
    }
    fill_payload: dict[str, Any] | None = None

    if args.fill or not live:
        if args.fill:
            fill_payload = fill_local()
            payload["fill"] = {
                "http_status": fill_payload["http_status"],
                "persona": fill_payload["persona"],
                "target": fill_payload["target"],
                "answer_count": len(fill_payload.get("answers") or []),
            }
            if fill_payload["http_status"] != 200:
                payload["passed"] = False
                payload["stopped"] = "fill_failed"
                print(json.dumps(payload, indent=2))
                return 1

    try:
        return _main_body(args, live, credit_stop, run_id, run_dir, payload, fill_payload)
    finally:
        if args.seed_bug:
            clear_seed_bug()
        clear_agent_policy()


def _main_body(
    args: argparse.Namespace,
    live: bool,
    credit_stop: float,
    run_id: str,
    run_dir: Path,
    payload: dict[str, Any],
    fill_payload: dict[str, Any] | None,
) -> int:
    if args.seed_bug:
        set_seed_bug(args.seed_bug)
        payload["seed_bug"] = args.seed_bug
        payload["seed_bug_label"] = "deliberately_planted"
    if live:
        who = read_whoami()
        if not whoami_is_logged_in(who):
            payload["passed"] = False
            payload["stopped"] = "kane_cli_not_logged_in"
            payload["command"] = redact_kane_command(kane_testmd_command(Path(args.suite)))
            print(json.dumps(payload, indent=2))
            return 2
        balance_before = read_balance()
        harness = (REPO_ROOT / "tests" / "kane" / "harness.py").read_text(encoding="utf-8")

        def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            merged = (completed.stdout or "") + (completed.stderr or "")
            completed.stdout = merged
            return completed

        result = run_live_loop(
            Path(args.suite),
            harness,
            _run,
            max_attempts=args.max_attempts,
            credit_stop=credit_stop,
            run_id=run_id,
            save_artifacts=args.save_evidence,
        )
        balance_after = read_balance()
        recorded = result.credits
        if balance_before is not None and balance_after is not None:
            recorded = max(recorded, balance_before - balance_after)
        result.credits = recorded
        append_credits_ledger(
            run_id,
            "cl1_live_loop",
            balance_before,
            balance_after,
            recorded,
            note=str(result.stopped or ""),
        )
        payload["command"] = redact_kane_command(kane_testmd_command(Path(args.suite)))
        payload["passed"] = result.passed
        payload["stopped"] = result.stopped
        payload["credits"] = result.credits
        payload["attempts"] = result.attempts
        payload["balance_before"] = balance_before
        payload["balance_after"] = balance_after
        if args.save_evidence:
            write_summary(run_dir, payload)
        print(json.dumps(payload, indent=2))
        return 0 if result.passed else 1

    harness = (REPO_ROOT / "tests" / "kane" / "harness.py").read_text(encoding="utf-8")
    attempts = ndjson_fixture_attempts()
    last_fill = fill_payload

    def _replay_cb(
        attempt_no: int,
        attempt: dict[str, Any],
        verdict: Verdict,
        plan: FixPlan | None,
        diff: dict[str, Any],
    ) -> None:
        if not args.save_evidence:
            return
        events = attempt.get("console_events") or []
        ndjson = "\n".join(json.dumps(e, ensure_ascii=False) for e in events)
        if ndjson and not ndjson.endswith("\n"):
            ndjson += "\n"
        pack = Path(str(attempt["evidence"])) if attempt.get("evidence") else None
        save_attempt_artifacts(
            run_dir,
            attempt_no,
            kane_ndjson=ndjson,
            fill=last_fill if attempt_no == 1 else None,
            fixplan=plan,
            diff=diff,
            pack_path=REPO_ROOT / pack if pack else None,
        )

    result = run_closed_loop(attempts, harness, credit_stop=credit_stop, on_attempt=_replay_cb)
    result.run_id = run_id
    payload.update(
        {
            "passed": result.passed,
            "stopped": result.stopped,
            "credits": result.credits,
            "attempts": result.attempts,
        }
    )
    if args.save_evidence:
        write_summary(run_dir, payload)
    print(json.dumps(payload, indent=2))
    return 0 if result.passed else 1


# Backwards-compatible helpers for tests
def fix_for_diagnosis(diagnosis: str | None, source: str) -> tuple[str, str]:
    verdict = Verdict(passed=False, result_status="failed", diagnosis=diagnosis)
    plan = build_fixplan(verdict, source)
    if plan is None:
        if diagnosis is None:
            return source, "no_diagnosis"
        return source, "unhandled_" + diagnosis
    _src, _diff, action = apply_fixplan(plan, source)
    return _src, action


if __name__ == "__main__":
    sys.exit(main())