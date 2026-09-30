"""One fixture-backed analysis flow; no model calls or purchase execution."""

from typing import Literal

from pydantic import BaseModel, Field

SAMPLE_TEXT = (
    "We want to buy Acme Analytics for the product team. It costs $1,200 per year "
    "for five users. We'll upload anonymized product usage data."
)
MANAGER_THRESHOLD_CENTS = 100_000  # Demo rule, not a real company policy.


class ProcurementRequest(BaseModel):
    request_text: str = Field(min_length=1)


class ProcurementAnalysis(BaseModel):
    vendor: str
    team: str
    annual_cost_cents: int = Field(ge=0)
    users: int = Field(gt=0)
    data_use: str
    external_data_upload: bool


class ReviewResponse(BaseModel):
    analysis_source: Literal["fixture"] = "fixture"
    analysis: ProcurementAnalysis
    status: Literal["requires_review", "eligible_under_demo_policy"]
    required_reviewers: list[str]
    rules_applied: list[str]
    reasons: list[str]
    missing_information: list[str]


def fixture_analysis(request: ProcurementRequest) -> ProcurementAnalysis:
    if request.request_text.strip() != SAMPLE_TEXT:
        raise ValueError("Only the Acme Analytics example is supported in fixture mode.")
    return ProcurementAnalysis(
        vendor="Acme Analytics",
        team="product",
        annual_cost_cents=120_000,
        users=5,
        data_use="Anonymized product usage data (requester's description; unverified)",
        external_data_upload=True,
    )


def evaluate_policy(analysis: ProcurementAnalysis) -> ReviewResponse:
    reviewers, rules, reasons = [], [], []
    if analysis.annual_cost_cents > MANAGER_THRESHOLD_CENTS:
        reviewers.append("manager")
        rules.append("DEMO-SPEND-1")
        reasons.append("Annual cost exceeds the demo $1,000 manager-review threshold.")
    if analysis.external_data_upload:
        reviewers.append("security")
        rules.append("DEMO-DATA-1")
        reasons.append("External data uploads require security review under the demo policy.")
    return ReviewResponse(
        analysis=analysis,
        status="requires_review" if reviewers else "eligible_under_demo_policy",
        required_reviewers=reviewers,
        rules_applied=rules,
        reasons=reasons,
        missing_information=(
            ["Confirm the data fields to be uploaded and how they are anonymized."]
            if analysis.external_data_upload else []
        ),
    )
