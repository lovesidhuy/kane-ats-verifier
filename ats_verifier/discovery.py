"""Cross-board job normalization, apply-type classification, and deduplication."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class RawJob:
    source_platform: str
    source_job_id: str
    title: str
    company: str
    location: str = ""
    description: str = ""
    listing_url: str = ""
    destination_url: str | None = None


@dataclass
class ApplyClassification:
    apply_type: str
    confidence: float
    source: str
    verification_required: bool
    confirmed: bool = False


@dataclass
class NormalizedJob:
    source_platform: str
    source_job_id: str
    discovery_engine: str
    query_id: str
    job_title: str
    company_name: str
    location: str
    description: str
    listing_url: str
    destination_url: str | None = None
    apply_type: str = "UNKNOWN"
    source_refs: list[dict[str, str]] = field(default_factory=list)


_EXTERNAL_ATS_DOMAINS = (
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "bamboohr.com",
    "myworkdayjobs.com",
)


def classify_apply_type(job: NormalizedJob) -> ApplyClassification:
    host = (urlparse(job.destination_url or job.listing_url).hostname or "").lower()
    if any(host == dom or host.endswith("." + dom) for dom in _EXTERNAL_ATS_DOMAINS):
        return ApplyClassification(
            apply_type="COMPANY_APPLY",
            confidence=0.9,
            source=f"external_ats:{host}",
            verification_required=False,
            confirmed=True,
        )
    if job.source_platform in {"indeed", "linkedin", "workopolis"}:
        return ApplyClassification(
            apply_type="EASY_APPLY",
            confidence=0.85,
            source=f"{job.source_platform}_board",
            verification_required=False,
            confirmed=True,
        )
    return ApplyClassification(
        apply_type="UNKNOWN",
        confidence=0.0,
        source="unverified",
        verification_required=True,
        confirmed=False,
    )


def normalize_raw_job(
    raw: RawJob,
    *,
    discovery_engine: str = "harness",
    search_term: str = "",
    location: str = "",
) -> NormalizedJob:
    query_id = f"{search_term.strip().lower()}_{location.strip().lower()}".strip("_") or "default"
    job = NormalizedJob(
        source_platform=raw.source_platform.strip().lower(),
        source_job_id=str(raw.source_job_id).strip(),
        discovery_engine=discovery_engine,
        query_id=query_id,
        job_title=re.sub(r"\s+", " ", raw.title.strip()),
        company_name=re.sub(r"\s+", " ", raw.company.strip()),
        location=re.sub(r"\s+", " ", raw.location.strip()),
        description=raw.description,
        listing_url=raw.listing_url.strip(),
        destination_url=raw.destination_url,
        source_refs=[
            {"platform": raw.source_platform.strip().lower(), "job_id": str(raw.source_job_id).strip()}
        ],
    )
    job.apply_type = classify_apply_type(job).apply_type
    return job


def deduplicate(jobs: list[NormalizedJob]) -> list[NormalizedJob]:
    """Deduplicate normalized jobs by platform+id and normalized (company, title, location)."""
    seen_ids: dict[str, NormalizedJob] = {}
    seen_ctl: dict[str, NormalizedJob] = {}
    unique: list[NormalizedJob] = []

    for job in jobs:
        pid = f"{job.source_platform}:{job.source_job_id}"
        ctl = "|".join(
            [
                job.company_name.strip().lower(),
                job.job_title.strip().lower(),
                job.location.strip().lower(),
            ]
        )
        winner = seen_ids.get(pid) or seen_ctl.get(ctl)
        if winner is not None:
            for ref in job.source_refs:
                if ref not in winner.source_refs:
                    winner.source_refs.append(ref)
            continue
        seen_ids[pid] = job
        seen_ctl[ctl] = job
        unique.append(job)

    return unique
