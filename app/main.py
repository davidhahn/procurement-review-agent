from fastapi import FastAPI, HTTPException

from app.procurement import (
    ProcurementRequest,
    ReviewResponse,
    evaluate_policy,
    fixture_analysis,
)

app = FastAPI(title="Procurement Review Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/requests/analyze", response_model=ReviewResponse)
def analyze_request(body: ProcurementRequest) -> ReviewResponse:
    try:
        analysis = fixture_analysis(body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return evaluate_policy(analysis)
