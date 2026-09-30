# Procurement Review Agent

This project explores how AI can prepare a software purchase review while keeping policy enforcement and approval under explicit control. An employee describes what they want to buy. The intended system extracts the relevant facts, checks company policy, and explains whether the request can proceed or needs human review.

Software purchase requests often arrive with incomplete information. Reviewing them means identifying missing details, checking spending and data security requirements, and determining who needs to approve an exception.

The central question:

> What can the system decide automatically, and when must a person take over?

## 1. Example workflow

**Planned behavior — procurement analysis is not implemented yet.**

An employee submits:

> We want to buy Acme Analytics for the product team. It costs $1,200 per year for five users. We'll upload anonymized product usage data.

The system prepares a review containing:

- **Purchase details:** the vendor, annual cost, team, number of users, and intended data use.
- **Missing information:** details needed to evaluate the request, such as whether the vendor is already approved and what the uploaded data contains.
- **Applicable policies:** the spending and data security rules relevant to the request, with references.
- **Recommended next step:** proceed under policy, request more information, or route to the required human reviewer, with reasons.

The outcome depends on the policy rules and available facts. Describing data as “anonymized” does not establish that it meets the company's requirements. A recommendation does not execute a purchase or record a human approval.

## 2. Decision boundaries

| Responsibility | Owner |
| --- | --- |
| Interpret the request and prepare structured analysis | AI |
| Enforce spending thresholds, required information, and review requirements | Application rules |
| Decide exceptions and provide required approvals | Human reviewer |

The model's interpretation is an input to the policy evaluator. It cannot override a rule or substitute its recommendation for a required human decision. Missing information should remain explicit instead of being filled in with assumptions.

## 3. Architecture

The planned request flow is:

```text
Request → Structured analysis → Policy evaluation → Recommendation / Human review
```

A FastAPI backend will coordinate the workflow. The first working version will use predefined fixture analysis and local policy files so the decision path can be exercised without a model call.

Later, an LLM will replace the fixture analysis and return the same structured output. The deterministic policy evaluator and API contract will remain in place.

## 4. Current status

The repository currently contains a minimal FastAPI app with a working `/health` endpoint and generated API documentation.

**Next milestone:** one complete fixture-based procurement review, from a submitted request to a response containing the analysis, applicable rules, and required next step.

Policy evaluation, LLM analysis, and a human review interface are not implemented yet.

## 5. Local setup

Requires Python 3.11 or later. Run these commands from the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open [the health endpoint](http://127.0.0.1:8000/health) or [the API docs](http://127.0.0.1:8000/docs).

```sh
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

No API keys, environment variables, or database are required. `.env.example` is a placeholder for future configuration.
