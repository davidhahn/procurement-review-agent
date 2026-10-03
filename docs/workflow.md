# Software procurement workflow

Planning baseline: 2026-10-02. This document defines the intended behavior before implementing the revised decision function. Today's changes are documentation only.

## What I want to be true

An employee can submit a software request, and application policy determines whether it may continue automatically or must wait for information or human approval.

The model can interpret the request and recommend what should happen. My code decides whether that recommendation can actually execute.

### Comparison with the planning notes

The starting statement above agrees with the [Human-in-the-Loop AI Project Plan](https://app.notion.com/p/3eb44d8aed6a81d180a5dd8c261d2563): interpretation belongs to AI; authority and execution belong to application code. The [technical planning notes](https://app.notion.com/p/3ec44d8aed6a8072a9dac1256b4610d7) add the working method: inspect what is true, identify an unproven claim, and derive expected results from policy before implementation.

The older plan contains conflicting examples: low spend both auto-approves and requires team-lead approval; threshold prose uses `< $2,500`, while its decision example uses `> $2,500`. It also includes rejection and broader infrastructure. Today's explicit brief takes precedence: use the rules and five actions below, no rejection, and prove a structured-input decision function first.

## What is true now

The procurement checkout was inspected at commit `5745484`. `app/procurement.py` already has a fixture analyzer and `evaluate_policy()`. The existing demo uses a $1,000 manager threshold and treats all external data uploads as requiring security review. Its sample returns `requires_review`.

That is a runnable earlier demonstration, not the new policy contract. It lacks a sensitive-data field, the new action names, and a missing-information-first decision. It does not persist workflow state or execute actions. No existing application code or tests were changed today.

The next step is to replace those demo assumptions deliberately, not to pretend no decision path exists. Structured extraction and policy evaluation are separate steps. The model proposes facts and recommendations; application code determines the permitted action.

## Users and input

- Employee: submits a software purchase request and supplies missing information.
- Reviewer: evaluates exceptions and provides the approvals required by policy.

The eventual entry point accepts free-form text. The next decision function receives already structured facts:

| Field | Meaning |
| --- | --- |
| `vendor` | Software/vendor name |
| `annual_cost` | Annual cost in USD; use decimal money or integer cents in implementation |
| `users` | Positive number of users |
| `purpose` | Why the software is needed |
| `data_access` | What data it accesses |
| `handles_sensitive_data` | Explicit true/false; unknown is missing, not false |

For the initial contract, these six fields are required. The application derives missing fields from absent/null/blank values; the AI's missing-information list is advisory. Zero cost and `false` are values, not missing fields. Invalid amounts or types must not silently reach auto-approval; exact validation-error formatting is deferred.

The three policy decision inputs are annual cost, sensitivity, and whether required information is missing. Vendor, purpose, users, and data description determine completeness; no vendor-risk or department-specific policy is being added.

## Responsibilities and authority

| AI responsibilities, later | Application responsibilities |
| --- | --- |
| Extract fields from free text | Validate the structured input and determine required fields |
| Identify missing information | Enforce missing-information and spend rules |
| Identify relevant policy | Enforce security, procurement, and finance requirements |
| Recommend an action and explain why | Decide whether execution is allowed |
| Prepare follow-up questions | Persist state, record approvals, and execute permitted actions |

The AI recommendation is not an authorization input. The target policy boundary is `evaluate_procurement(request)`. That function has no LLM calls, database access, or action execution. A later workflow service must consume its decision before invoking any action.

## Policy and output contract

Apply the following rules in order; the first matching rule selects the primary action.

| Priority | Condition | Action | Approval requirements |
| --- | --- | --- | --- |
| 1 | Required information missing | `REQUEST_INFORMATION` | None assigned at this step; re-evaluate after the employee responds |
| 2 | Sensitive data involved | `REQUIRE_SECURITY_REVIEW` | Security; combined spend requirements need the decision noted below |
| 3 | Annual cost > $10,000 | `REQUIRE_FINANCE_REVIEW` | Finance **and procurement** |
| 4 | Annual cost > $2,500 | `REQUIRE_PROCUREMENT_REVIEW` | Procurement |
| 5 | Otherwise | `AUTO_APPROVE` | None |

These are the only action types. There is no rejection rule yet.

The strict comparisons mean a complete, non-sensitive $2,500 request auto-approves; a $10,000 request requires procurement review; a $10,000.01 request requires finance and procurement. This follows today's rule text rather than the older plan's ambiguous ranges.

Output must contain:

- `action`: one of the five actions above.
- `reason`: an explanation tied to the selected written rule.
- `approval_requirements`: named reviewer roles, including both finance and procurement for high spend.

For `REQUEST_INFORMATION`, also expose the missing fields so the caller knows what to ask. Exact wording of reasons can evolve; action and approval requirements are fixed expectations.

### Human-review and execution boundary

The eventual flow is:

```text
Free text → structured extraction → policy lookup → recommendation
          → deterministic decision → safe local action OR persisted pause
```

`AUTO_APPROVE` permits a later local approval-state action. It does not prove that a purchase happened. Every review action blocks automatic execution until the required approvals have been recorded. `REQUEST_INFORMATION` also blocks execution and asks the employee for facts.

A real review workflow must save the request, analysis, policy decision, outstanding approvals, and history, then resume the same case after input or review. A response containing “review required” alone does not satisfy that requirement. Persistence and an executor are later work.

## First behavior I cannot verify yet

> I want the system to prevent risky requests from auto-executing under the intended procurement rules, but right now I cannot verify that the existing demo produces the new actions from structured cost, sensitivity, and completeness inputs—or that a review decision actually blocks an executor.

The immediate gap is policy correctness. The later gap is enforced pause/resume. Passing decision fixtures will prove the former only.

## Fixed requests and expected decisions

These are written acceptance fixtures, not newly implemented tests. Expected results come from the policy table above, not from current code. All money is annual USD. Sensitive-data labels are explicit fixture facts; “anonymized” text alone is not proof of non-sensitivity.

| ID | Vendor | Annual cost | Users | Purpose | Data access | Sensitive? | Expected action | Approval requirements |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-01 | Acme Analytics | $1,200 | 5 | Product analytics | Anonymized product usage data; no sensitive data in this fixture | false | `AUTO_APPROVE` | `[]` |
| P-02 | Team Planner | $5,000 | 20 | Plan internal projects | Public sample project data | false | `REQUIRE_PROCUREMENT_REVIEW` | `[procurement]` |
| P-03 | Design Library | $14,000 | 40 | Manage public design assets | Public design assets | false | `REQUIRE_FINANCE_REVIEW` | `[finance, procurement]` |
| P-04 | Customer Insights | $1,200 | 5 | Analyze customer activity | Customer email addresses | true | `REQUIRE_SECURITY_REVIEW` | `[security]` |
| P-05 | Acme Analytics | missing/null | 5 | Product analytics | Anonymized product usage data | false | `REQUEST_INFORMATION` | `[]`; missing field: `annual_cost` |

Reasons derived before implementation:

- P-01: all fields present, non-sensitive data, cost at or below $2,500.
- P-02: complete and non-sensitive; cost above $2,500 but not above $10,000.
- P-03: complete and non-sensitive; cost above $10,000 requires both approvals.
- P-04: complete; sensitivity takes priority over low spend.
- P-05: missing cost is checked before approval rules; do not substitute zero.

The original Acme free-text fixture does not explicitly assert non-sensitivity. P-01 adds that as a known structured fact for this decision-only exercise; it does not claim the current extractor establishes it.

## Exact next implementation task

Build the deterministic procurement decision function and prove it against the fixed requests above before adding an LLM:

```python
decision = evaluate_procurement(request)
```

1. Define structured input and typed decision output using the agreed fields/actions.
2. Replace the old demo policy assumptions with the ordered rules above.
3. Turn P-01 through P-05 into fixed tests; compare actions and approval requirements, and check useful reasons/missing fields.
4. Add threshold-edge checks at $2,500 and $10,000 and just above each; unknown sensitivity must request information rather than default to false.
5. Update the example/API adapter and outdated demo-policy documentation only as needed to expose the new result; keep the evaluator free of I/O.

The first vertical slice is done when P-01 moves through the structured-input decision path and returns `AUTO_APPROVE`, a policy reason, and no approvals. The task is complete when all five acceptance cases agree with the written expectations, without a network call or database, and the threshold checks also pass. That is not yet proof of extraction quality or a human-in-the-loop execution system.

## Unanswered questions and later work

- **Combined sensitivity and high spend:** the primary action is security review by precedence, but should its approval list accumulate finance/procurement too? Do not interpret a security approval as waiving spend approvals. Keep combined cases blocked from execution until this is defined; the initial fixtures isolate each rule.
- **Trust in sensitivity:** who confirms an extracted sensitivity label before real execution? A model's `false` alone is not verification. Today's fixtures deliberately bypass this uncertainty.
- **Execution meaning:** what exact local state change does auto-approval make, and how will retries avoid duplicate actions? Not needed to prove the decision function.
- **Validation contract:** how should invalid structured types/negative costs be reported versus genuinely missing information? Define that when adding typed inputs; neither should auto-approve.
- **Deferred product rules:** vendor risk, budgets, contracts, duplicate tooling, SOC 2, legal review, and rejection need explicit decisions before entering policy.
- **Not today:** LLM extraction, agent frameworks, reviewer UI, Postgres workflow state, vector storage, integrations, Slack/email, auth/RBAC, large eval suites, and frontend scaffolding.
