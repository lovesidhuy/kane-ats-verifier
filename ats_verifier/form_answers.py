"""Deterministic candidate profile and screening-policy answer resolver."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass
class ResolvedAnswer:
    value: str
    source: str
    score: float = 1.0
    matched_question: str = ""


def load_profile() -> dict[str, Any]:
    """Return the deterministic synthetic candidate profile used for dry-run verification."""
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "full_name": "Jane Doe",
        "email": "user@example.com",
        "phone": "5550199",
        "city": "Surrey",
        "state": "BC",
        "zipcode": "V6B 1A1",
        "country": "Canada",
        "location": "Surrey, BC, Canada",
        "school": "Kwantlen Polytechnic University",
        "school_short": "KPU",
        "graduation_year": "2026",
        "linkedin": "https://linkedin.com/in/example",
        "website": "https://example.com/portfolio",
        "years_of_experience": "3",
        "require_visa": "No",
        "desired_salary": "70000",
        "salary_expectation": "145000",
        "clearance": "No",
        "cover_letter": (
            "I am excited to bring hands-on cloud infrastructure, QA automation, "
            "and reliability engineering experience to your team."
        ),
        "why_company_answer": (
            "Built deterministic browser verification and automated reliability checks "
            "that catch policy mismatches and broken selectors prior to release."
        ),
        "current_company": "Independent Engineering",
        "current_title": "Systems Engineer",
    }


def resolve_answer(
    question: str,
    options: Iterable[str] | None = None,
    job_context: str = "",
    profile: dict[str, Any] | None = None,
    allow_ai: bool = False,
) -> ResolvedAnswer:
    """Resolve a screening question strictly from deterministic profile and policy rules."""
    del options, job_context, allow_ai
    prof = profile if profile is not None else load_profile()
    q = (question or "").strip().lower()

    if "authorized to work" in q or "work authorization" in q or "legally authorized" in q:
        val = str(prof.get("work_auth") or "Yes")
        return ResolvedAnswer(value=val, source="policy_auth_ca", score=1.0, matched_question=question)

    if "sponsorship" in q or "require visa" in q or "visa" in q:
        val = str(prof.get("sponsorship") or prof.get("require_visa") or "No")
        return ResolvedAnswer(value=val, source="policy_visa", score=1.0, matched_question=question)

    if "years" in q and ("python" in q or "experience" in q):
        val = str(prof.get("years_of_experience") or "3")
        return ResolvedAnswer(value=val, source="policy_years", score=1.0, matched_question=question)

    if "salary" in q or "compensation" in q:
        val = str(prof.get("salary_expectation") or prof.get("desired_salary") or "70000")
        return ResolvedAnswer(value=val, source="policy_salary", score=1.0, matched_question=question)

    if "clearance" in q:
        val = str(prof.get("clearance") or "No")
        return ResolvedAnswer(value=val, source="policy_clearance", score=1.0, matched_question=question)

    if "interested" in q or "why" in q or "challenging" in q or "problem" in q:
        val = str(prof.get("why_company_answer") or prof.get("cover_letter") or "")
        return ResolvedAnswer(value=val, source="policy_behavioral", score=0.95, matched_question=question)

    return ResolvedAnswer(value="", source="policy_unmatched", score=0.0, matched_question=question)
