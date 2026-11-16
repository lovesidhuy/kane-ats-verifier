"""V-3: prove Kane-oriented assertions fail when the agent/harness is broken (local, no credits)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_harness():
    harness_path = REPO_ROOT / "tests" / "kane" / "harness.py"
    spec = importlib.util.spec_from_file_location("jobsfarm_kane_harness_mut", harness_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_mutation_visa_persona_must_answer_yes_without_seed():
    """Baseline: visa persona policy is Yes (breaking this should fail suite 17)."""
    mod = _load_harness()
    client = mod.app.test_client()
    response = client.post(
        "/api/resolve-fields",
        json={
            "persona": "visa_sponsorship",
            "job_context": "mutation",
            "fields": [
                {
                    "id": "sponsorship",
                    "label": "Will you now or in the future require visa sponsorship?",
                    "type": "select",
                }
            ],
        },
    )
    assert response.status_code == 200
    answers = response.get_json().get("answers") or []
    val = next((a.get("value") for a in answers if a.get("id") == "sponsorship"), None)
    assert val == "Yes"


def test_mutation_seed_bug_forces_no_even_when_agent_not_fixed():
    import scripts.kane_loop as kane_loop

    kane_loop.clear_seed_bug()
    kane_loop.clear_agent_policy()
    kane_loop.set_seed_bug("visa_wrong_answer")
    try:
        fill = kane_loop.fill_local(persona="visa_sponsorship")
        val = next(
            (a.get("value") for a in fill["answers"] if a.get("id") == "sponsorship"),
            None,
        )
        assert val == "No"
    finally:
        kane_loop.clear_seed_bug()


def test_mutation_network_guard_off_allows_disabled_banner():
    mod = _load_harness()
    client = mod.app.test_client()
    on = client.get("/tools/network-guard-test").get_data(as_text=True)
    off = client.get("/tools/network-guard-test?guard=off").get_data(as_text=True)
    assert "NETWORK_SUBMIT_GUARD_DISABLED" not in on
    assert "NETWORK_SUBMIT_GUARD_DISABLED" in off