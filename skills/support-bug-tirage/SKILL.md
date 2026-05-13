---

name: support-bug-triage

description: Triage support emails into product bugs, data/configuration issues, support-only follow-ups, or insufficient evidence, then investigate and optionally create narrow fixes. Use when reviewing Gmail support threads, debugging customer-reported bugs, deciding whether a report deserves a PR, or preparing evidence-backed PR descriptions from support incidents.

---

# Support Bug Triage

Use this skill to turn support emails into careful engineering action without overfitting one customer's report.

## Workflow

1. **Find the report**

- Search Gmail for recent support threads and read the full thread when a message suggests broken product behavior.

- Capture the customer-facing symptom, account identifiers, timestamps, and the canonical Gmail or Google Groups thread link.

2. **Classify first**

- Product bug: code behavior is likely wrong or brittle.

- Data/configuration issue: customer-specific state, permissions, billing setup, imports, or integrations need repair.

- Support-only issue: the right action is explanation, billing/admin change, or customer guidance.

- Insufficient evidence: more customer details, logs, screenshots, or repro steps are needed.

3. **Investigate credible bugs**

- Trace the user-facing flow in code before editing.

- Check production evidence when available, especially Datadog logs/traces around the customer timestamp.

- Compare the report, logs, and code path. Do not infer a code bug from the email alone.

4. **Decide whether to fix**

- Create a PR only when the bug is reproducible from evidence, the code change is narrow, and the expected behavior is clear.

- Prefer no PR when the issue is data repair, support action, unclear evidence, or broad product ambiguity.

## PR Requirements

When opening a PR from a support incident, the description must include:

- Support thread link, preferably the Google Groups or Gmail canonical URL.

- What happened and how it could happen again.

- Why the fix prevents recurrence.

- Code trace with GitHub permalinks pinned to the PR head commit.

- Production evidence links, such as Datadog logs or traces, with the key fields summarized.

- Alternatives considered and why they were rejected.

- Focused test plan and any validation gaps.

## Guardrails

- Keep customer-specific data minimal and relevant; avoid copying long email bodies.

- Do not create a code fix just to mask bad data unless the code path is also wrong.

- Do not run destructive repair actions or send customer replies without explicit user approval.

- Keep PRs small. If investigation reveals multiple bugs, split or report follow-up work.