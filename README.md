# Procurement Review Agent

This project explores how AI can prepare a software purchase review while keeping policy enforcement and approval under explicit control. An employee describes what they want to buy. The intended system extracts the relevant facts, checks company policy, and explains whether the request can proceed or needs human review.

Software purchase requests often arrive with incomplete information. Reviewing them means identifying missing details, checking spending and data security requirements, and determining who needs to approve an exception.

The central question:

> What can the system decide automatically, and when must a person take over?

## 1. Example workflow

**The example below now runs locally with fixture analysis and two demo policy rules. General request analysis remains planned.**

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

The local request flow is:

```text
Request → Structured analysis → Policy evaluation → Recommendation / Human review
```

A FastAPI backend coordinates the workflow. The current version recognizes one example, returns predefined structured analysis, and evaluates two rules in Python without a model call. Separate policy files will follow when the rules expand.

Later, an LLM will replace the fixture analysis and return the same structured output. The deterministic policy evaluator and API contract will remain in place.

## 4. Current status

The backend exposes `/health` and `POST /requests/analyze`. The Acme Analytics fixture returns `requires_review`, routes to a manager and security reviewer, and asks for clarification of the uploaded data.

Two illustrative rules drive that result: annual cost over $1,000 requires manager review (`DEMO-SPEND-1`); external data uploads require security review (`DEMO-DATA-1`). These are demo assumptions, not a real company's policies. No purchase or approval is executed.

Only the exact sample text (ignoring surrounding whitespace) is supported. Other requests return HTTP 422. There is no LLM, database, or human review interface yet.

**Next milestone:** add a second, lower-cost example with no external data upload to exercise the other decision path.

See [the day-one checklist and run notes](docs/day-one.md).

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

### Run the procurement example

With the server running, open another terminal at the repository root:

```sh
curl -sS http://127.0.0.1:8000/requests/analyze \
  -H 'Content-Type: application/json' \
  --data-binary @examples/acme-request.json
```

Expected: `status: "requires_review"`, with `manager` and `security` in `required_reviewers`, both demo rule IDs, and a question about data anonymization.

Check an unsupported request:

```sh
curl -i http://127.0.0.1:8000/requests/analyze \
  -H 'Content-Type: application/json' \
  -d '{"request_text":"Buy another tool"}'
```

Expected: HTTP 422 with an explanation that only the Acme Analytics example is supported.

### Run the checks

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```
