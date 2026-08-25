# Lab 1: Requirements Engineering & UML Use-Case Modelling

**Course:** Software Engineering (PES University, Dept. of CSE)
**Duration:** 90 minutes
**Problem Statement #46 — Developer Tools & IT Operations**

## 1. Objective

From the short scenario provided by the instructor, elicit key functions and constraints;
write clear, verifiable functional (FR) and nonfunctional (NFR) requirements; then translate
them into a UML use-case diagram and one detailed use-case flow.

## 2. Problem Statement: Remote Team Time-Tracking & Project Approver

**Context:** An engineering productivity platform that tracks developer hours against Jira
tickets, monitors project budget burn rates, and facilitates managerial timesheet approval
workflows.

**Stakeholders / Actors:**
- **Remote Developer** — logs time against tasks and submits timesheets.
- **Engineering Manager** — reviews, approves/rejects timesheets, and monitors budget burn.
- **Jira System** *(external system actor)* — source of truth for project tickets, referenced
  when developers log time and the system syncs entries against it.

## 3. Approach

1. **Elicitation** — Brainstormed the functions a remote time-tracking/approval tool needs
   (logging time, submitting for approval, manager review, Jira sync, budget visibility) and
   the constraints around them (daily hour caps, dashboard latency, self-approval prevention).
2. **Requirements drafting** — Converted each function/constraint into a testable "The system
   shall…" statement with a measurable pass/fail acceptance criterion, a priority, and a
   rationale (see `Requirements_Table.xlsx`).
3. **Actor & use-case extraction** — From the approved requirements, identified 3 actors and
   8 use cases (see diagram below), including one `«include»` relationship (a use case that
   always triggers a sub-behaviour) and one `«extend»` relationship (a use case that
   conditionally adds optional behaviour).
4. **Use-case diagram** — Modelled actors, the system boundary, use cases, associations, and
   the `«include»`/`«extend»` dependencies.
5. **Use-case flow** — Wrote a full flow specification (preconditions, postconditions, main
   success scenario, and one alternate flow) for the core use case: **Approve Timesheet**.

## 4. Deliverables in this Folder

| File | What it contains |
|---|---|
| [`Requirements_Table.xlsx`](Requirements_Table.xlsx) | 5 Functional Requirements (FR-001–FR-005) and 2 Non-Functional Requirements (NFR-001–NFR-002). Each row has: Req ID, Type, Description, Priority, Acceptance Criteria, Rationale. |
| [`UML_UseCase_Diagram.pdf`](UML_UseCase_Diagram.pdf) | Use-case diagram with 3 actors, 8 use cases inside the system boundary, associations, and both an `«include»` and an `«extend»` relationship. |
| [`UseCase_Flow_ApproveTimesheet.docx`](UseCase_Flow_ApproveTimesheet.docx) / [`.pdf`](UseCase_Flow_ApproveTimesheet.pdf) | One-page flow specification for **UC-05: Approve Timesheet** — Preconditions, Postconditions, Main Success Scenario, and Alternate Flow (rejection path). Provided in both Word and PDF as required. |

## 5. Requirements Summary

| Req ID | Type | Priority | Summary |
|---|---|---|---|
| FR-001 | Functional | High | Log time against tasks; block any single day's total from exceeding 24 hours. *(given)* |
| FR-002 | Functional | High | Developer submits a completed weekly timesheet to their manager for approval. |
| FR-003 | Functional | High | Manager approves/rejects a timesheet; rejection requires a comment. |
| FR-004 | Functional | Medium | Time entries are synced to Jira ticket IDs; entries against nonexistent tickets are rejected. |
| FR-005 | Functional | High | System computes and displays real-time project budget burn rate. |
| NFR-001 | Nonfunctional (Performance & Security) | High | Approval status/budget dashboards update within 500 ms under peak load. *(given)* |
| NFR-002 | Nonfunctional (Security) | High | Role-based access control: a developer cannot approve/reject their own timesheet. |

Full descriptions, acceptance criteria, and rationale are in `Requirements_Table.xlsx`.

## 6. Use Cases Modelled

| ID | Use Case | Actor(s) | Relationship |
|---|---|---|---|
| UC-01 | Log Time Entry | Remote Developer | `«include»`s UC-03 |
| UC-02 | Submit Timesheet | Remote Developer | `«include»`s UC-04 |
| UC-03 | Sync Jira Ticket | Remote Developer, Jira System | included by UC-01 |
| UC-04 | Validate Timesheet Entries | Remote Developer | included by UC-02 |
| UC-05 | Approve Timesheet | Engineering Manager | `«extend»`ed by UC-07 |
| UC-06 | Reject Timesheet | Engineering Manager | — |
| UC-07 | Flag Budget Overrun | Engineering Manager | `«extend»`s UC-05 (conditional, when projected burn > 90%) |
| UC-08 | View Budget Burn Rate | Engineering Manager | — |

**Why `«include»`:** Logging a time entry and submitting a timesheet always require Jira-ticket
validation and entry validation respectively — these sub-behaviours are mandatory, so they are
modelled as `«include»`.

**Why `«extend»`:** Flagging a budget overrun only happens conditionally — when approving a
timesheet would push the project's budget burn past a threshold — so it's modelled as an
optional `«extend»` on **Approve Timesheet**.

## 7. Use-Case Flow: Approve Timesheet (UC-05)

- **Primary actor:** Engineering Manager
- **Preconditions:** Manager is authenticated; a developer's timesheet is in "Pending Approval"
  status and has already passed entry validation and the daily-hour-cap check.
- **Main success scenario:** Manager opens pending approvals → reviews a timesheet's hours and
  linked Jira tickets → approves it → system re-validates hour limits, checks for a budget
  overrun (triggering UC-07 if the burn rate would exceed 90%), marks the timesheet
  "Approved", recalculates the project's budget burn rate within 500 ms, and notifies the
  developer.
- **Alternate flow (A1 — Timesheet Rejected):** Manager rejects instead of approving; a
  rejection comment is mandatory; the timesheet is marked "Rejected" and the developer is
  notified and may revise and resubmit.

Full step-by-step detail is in `UseCase_Flow_ApproveTimesheet.pdf` / `.docx`.
