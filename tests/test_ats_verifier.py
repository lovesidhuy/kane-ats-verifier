"""Unit tests for the standalone ats_verifier package and harness alignment."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from ats_verifier.discovery import RawJob, deduplicate, normalize_raw_job
from ats_verifier.dom_autofill import DOMAutofillEngine, INJECT_VALUES_JS, SCAN_FIELDS_JS
from ats_verifier.form_answers import load_profile, resolve_answer

HARNESS = Path(__file__).resolve().parents[1] / "tests" / "kane" / "harness.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("kane_harness_standalone", HARNESS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_profile_and_qa_resolution_deterministic():
    profile = load_profile()
    assert profile["email"] == "user@example.com"
    assert resolve_answer("Are you legally authorized to work in Canada?", profile=profile).source == "policy_auth_ca"
    assert resolve_answer("Will you now or in the future require sponsorship?", profile=profile).value == "No"
    years = resolve_answer("How many years of Python experience do you have?", profile=profile)
    assert years.value == "3"
    assert years.source == "policy_years"


def test_dom_autofill_resolves_profile_and_policy_fields():
    profile = load_profile()
    fields = [
        {"id": "first_name", "label": "First Name", "type": "text", "current_value": ""},
        {"id": "email", "label": "Email", "type": "email", "current_value": ""},
        {"id": "sponsorship", "label": "Will you require sponsorship?", "type": "select", "current_value": ""},
    ]
    answers = DOMAutofillEngine.resolve_field_answers(fields, profile)
    by_id = {a["id"]: a["value"] for a in answers}
    assert by_id["first_name"] == "Jane"
    assert by_id["email"] == "user@example.com"
    assert by_id["sponsorship"] == "No"
    assert "data-ats-field-id" in SCAN_FIELDS_JS
    assert "dispatchEvent" in INJECT_VALUES_JS


def test_discovery_normalizer_and_dedupe_counts():
    raw = [
        RawJob("greenhouse", "1", "Cloud Engineer", "NorthStar Cloud", "Vancouver, BC", listing_url="https://boards.greenhouse.io/northstar/jobs/1"),
        RawJob("indeed", "abc", "Cloud Engineer", "NorthStar Cloud", "Vancouver, BC", listing_url="https://ca.indeed.com/viewjob?jk=abc"),
        RawJob("lever", "2", "Platform SRE", "Apex Systems", "Toronto, ON", listing_url="https://jobs.lever.co/apex/2"),
    ]
    norm = [normalize_raw_job(r, discovery_engine="harness") for r in raw]
    uniq = deduplicate(norm)
    assert len(uniq) == 2
    assert uniq[0].apply_type == "COMPANY_APPLY"


def test_harness_routes_smoke():
    mod = _load_harness()
    client = mod.app.test_client()
    assert client.get("/").status_code == 200
    assert client.get("/ats/greenhouse").status_code == 200
    qa = client.post("/api/resolve-qa", json={"question": "How many years of Python experience do you have?"})
    assert qa.status_code == 200
    assert qa.get_json()["value"] == "3"
    assert qa.get_json()["source"] == "policy_years"
    ded = client.post("/api/run-dedupe", json={})
    assert ded.status_code == 200
    assert ded.get_json()["raw_count"] == 5
    assert ded.get_json()["unique_count"] == 3
