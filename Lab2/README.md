# Lab 2: Agile Backlog Creation & Sprint Simulation in Jira

**Course:** Software Engineering (PES University, Dept. of CSE)
**Builds on Lab 1 — Problem Statement #46:** *Remote Team Time-Tracking & Project Approver*
(engineering-productivity platform: developers log hours against Jira tickets, managers approve
weekly timesheets, project budget burn-rate is monitored).

## 1. Objective

Convert the Lab 1 functional requirements into an Agile backlog (Epics → User Stories), prioritise
it, estimate it with story points (Fibonacci scale + Planning Poker), run two one-week sprints on a
Scrum board (To Do → In Progress → Done), and analyse progress with burndown charts.

## 2. Live Jira workspace (primary artifact for evaluation)

| | |
|---|---|
| Site | `sonuaadish0706as.atlassian.net` |
| Project | **Remote Time Tracker** (key `RTT`) — company-managed **Scrum** |
| Board | RTT board (id 35) — Backlog, Active sprints, Reports |

Ready for review in the workspace:
- **Backlog** with 4 Epics and 14 User Stories grouped by Epic.
- **Story points** on every story (Backlog → *More fields* → *Story Points*).
- **Two completed sprints** — Reports → *Sprint Report*.
- **Burndown charts** — Reports → *Burndown Chart* for *RTT Sprint 1* and *RTT Sprint 2*.

## 3. Deliverables in this folder

| File | Contents |
|---|---|
| [`Lab2_Agile_Backlog_Sprint_Report.pdf`](Lab2_Agile_Backlog_Sprint_Report.pdf) | Full report: requirement→backlog traceability, the 4 Epics, the 14-story product backlog (As-a/I-want/So-that, priority, story points, sprint, final status), Fibonacci + Planning Poker estimation, prioritisation rationale, Sprint 1 & Sprint 2 simulations with the **Jira burndown charts** and Sprint Report embedded, velocity, and the 4 reflection questions answered. |
| [`screenshots/`](screenshots/) | The raw Jira screenshots referenced by the report: backlog + Epic panel, story points, active-sprint board, Sprint 1 & Sprint 2 burndown charts, Sprint Report. |

## 4. Epics

| Epic | Name | Requirements | Stories / SP |
|---|---|---|---|
| RTT-1 | Time Logging & Jira Integration | FR-001, FR-004 (UC-01, UC-03) | 4 / 13 |
| RTT-2 | Timesheet Submission & Validation | FR-002 (UC-02, UC-04) | 3 / 8 |
| RTT-3 | Managerial Timesheet Approval | FR-003, NFR-002 (UC-05, UC-06) | 4 / 13 |
| RTT-4 | Project Budget Monitoring | FR-005, NFR-001 (UC-07, UC-08) | 3 / 18 |

**Backlog total:** 14 user stories, 52 story points.

## 5. Sprint simulation summary

| | Committed SP | Completed SP | Stories done | Velocity |
|---|---|---|---|---|
| Sprint 1 (RTT-1 + RTT-2) | 21 | 16 | 5 / 7 | 16 |
| Sprint 2 (RTT-3 + RTT-4 + carry-over) | 36 | 23 | 7 / 9 | 23 |
| **Project** | 52 | 39 (75%) | 12 / 14 | avg ~19.5 |

Carried past both sprints: RTT-17 (dashboard < 500 ms, 8 SP) and RTT-18 (90% budget-overrun
warning, 5 SP) — ~one more sprint of work.

Key insight from the burndowns: both lines finished **above** the ideal guideline, so both sprints
were over-committed; sustainable capacity is ~16–20 SP per one-week sprint.
