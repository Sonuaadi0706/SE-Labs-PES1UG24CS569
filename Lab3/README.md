# Lab 3: Component Modelling & Architectural Pattern Selection

**Course:** Software Engineering (PES University, Dept. of CSE)
**Duration:** 60 minutes
**Builds on Lab 1 — Problem Statement #46:** *Remote Team Time-Tracking & Project Approver*
(engineering-productivity platform: developers log hours against Jira tickets, managers approve
weekly timesheets, project budget burn-rate is monitored).

## 1. Objective

Evaluate architectural styles (Layered, Microservices, Client-Server), select the most appropriate
one for the assigned scenario, and produce a UML Component Diagram showing components, provided/
required interfaces, and dependencies.

## 2. Architecture Selection

**We chose Microservices Architecture for the Remote Team Time-Tracking & Project Approver System.**

Full reasoning — two scenario-specific reasons, one security advantage, and one performance
benefit — is in [`Lab3_Architecture_Justification.pdf`](Lab3_Architecture_Justification.pdf) /
[`.docx`](Lab3_Architecture_Justification.docx). In short:

- **Independent scaling for uneven load** — the budget dashboard (NFR-001, < 500 ms under peak
  load) and continuous time-entry logging have very different traffic shapes and scale
  independently as separate services, which a Layered or Client-Server design cannot do below the
  level of the whole application/server tier.
- **Fault isolation around Jira** — Jira sync (FR-004) is an external, third-party dependency.
  Isolating it in its own service means a Jira outage only degrades ticket syncing, not time
  logging or approvals.

## 3. Components Identified

| # | Component | Responsibility | Traces to |
|---|---|---|---|
| 1 | Client Application | Web/touch UI for developers & managers | — |
| 2 | API Gateway | AuthN, routing, rate limiting, RBAC enforcement at the perimeter | NFR-002 |
| 3 | Time Tracking Service | Log time entries; enforce the 24 h/day cap | FR-001 |
| 4 | Timesheet Approval Service | Submit / approve / reject timesheets; RBAC (no self-approval) | FR-002, FR-003, NFR-002 |
| 5 | Budget Monitoring Service | Compute & serve real-time project budget burn rate | FR-005, NFR-001 |
| 6 | Jira Integration Service | Sync time entries against Jira ticket IDs | FR-004 |
| 7 | Notification Service | Notify developers of approval/rejection outcomes | UC-05 flow (Lab 1) |
| 8 | Timesheet Database | Persists timesheets, time entries, and the budget ledger | — |
| — | Jira System *(external)* | Third-party system of record for tickets | External actor (Lab 1) |

8 internal components (5 required, 3 extra for a realistic microservices decomposition) plus the
external Jira System actor carried over from the Lab 1 use-case model.

## 4. Interfaces Modelled

9 provided/required interfaces are shown (4 required minimum) using ball (provided) and socket
(required) UML notation:

| Interface | Provider → Consumer | Purpose |
|---|---|---|
| `IWebAPI` | API Gateway → Client Application | Client's REST/HTTPS entry point |
| `ITimeLogging` | Time Tracking Service → API Gateway | Log time entries |
| `IApprovalWorkflow` | Timesheet Approval Service → API Gateway | Submit / approve / reject timesheets |
| `IBudgetDashboard` | Budget Monitoring Service → API Gateway | Real-time burn-rate feed |
| `IJiraSync` | Jira Integration Service → Time Tracking Service | Push time entries against Jira ticket IDs |
| `IJiraREST` | Jira System *(external)* → Jira Integration Service | Third-party Jira REST API |
| `INotify` | Notification Service → Timesheet Approval Service | Approval/rejection notifications |
| `IBudgetCheck` | Budget Monitoring Service → Timesheet Approval Service | Burn-rate check during approval (UC-07, > 90 %) |
| `IPersistence` | Timesheet Database → Time Tracking / Approval / Budget Monitoring services | Shared data access |

## 5. Deliverables in this Folder

| File | Contents |
|---|---|
| [`Component_Diagram.png`](Component_Diagram.png) | UML component diagram — 8 internal components + 1 external system, 9 provided/required interfaces, `<<component>>` stereotype notation with ball-and-socket connectors and `<<use>>`-style dependency routing. |
| [`Lab3_Architecture_Justification.docx`](Lab3_Architecture_Justification.docx) / [`.pdf`](Lab3_Architecture_Justification.pdf) | One-page justification: architecture selection statement, two scenario-specific reasons, one security advantage, one performance benefit. Provided in both Word and PDF as required. |
