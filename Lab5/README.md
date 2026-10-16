# Lab 5 — Static Code Analysis

**Course:** Software Engineering (PES University, Dept. of CSE) · **Student:** PES1UG24CS569 · **Lab:** 5 — Static Code Analysis

| | |
|---|---|
| Assigned repository (L5 #20 — Scholarship Disbursement) | https://github.com/SETAPESU26/L5_20_scholarship_disbursement |
| Personal submission repository | https://github.com/Sonuaadi0706/SE-Labs-PES1UG24CS569 |

## Objective

Use three static analysis tools to find and fix quality, security and style problems in the assigned Python program, a scholarship-office ledger (`scholarship_disbursement.py`), without changing what it does.

| Tool | Role | Before | After |
|---|---|---|---|
| **Pylint** | code quality and logic | 5.00 / 10 (16 messages) | **10.00 / 10** |
| **Bandit** | security | 4 issues (1 Medium, 3 Low) | **0 issues** |
| **Flake8** | PEP 8 style | 6 violations | **0 violations** |

The program's output is identical before and after:

```
50000 None
1 50000
archiving awards
```

## Highlights

- **SQL injection (Bandit B608, Medium)** — `grant()` built its `INSERT` with `%` string formatting; it now uses `?` placeholders.
- **Mutable default argument (Pylint W0102)** — `audit=[]` was shared across calls; it is now `audit=None`.
- **Global state (Pylint W0603)** — the `global disbursed_total` is gone; the total is derived from the database.
- **Silent failure and shell call (Bandit B110, B605, B607; Pylint W0718)** — removed the `try/except/pass` and the `os.system` call.
- **Double payout** (found by reading, not reported by a tool) — an award can no longer be disbursed twice.

The full table of 11 tool-reported issue groups and 2 extra findings is in [`issues.md`](issues.md).

## Commits

One commit per tool, as the handout asks, preceded by a baseline commit so every diff is readable and followed by a documentation commit.

| # | Commit | Result |
|---|---|---|
| 0 | Add assigned script and baseline reports | original code, "before" reports |
| 1 | Fix all Bandit findings | Bandit 4 → 0 |
| 2 | Fix Pylint findings | Pylint 5.00 → 10.00 |
| 3 | Fix all Flake8 findings and add after-reports | Flake8 6 → 0 |
| 4 | Add issue table, reflection and Lab 5 README | documentation |

## Deliverables

| Deliverable | File |
|---|---|
| Cleaned script (at least 4 issues fixed — all of them are) | [`scholarship_disbursement.py`](scholarship_disbursement.py) |
| Issue table | [`issues.md`](issues.md) |
| Reflection answers | [`reflection.md`](reflection.md) |
| Reports before | [`reports/before/`](reports/before/) — `pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt` |
| Reports after | [`reports/after/`](reports/after/) — `pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt` |

## Reproduce

```bash
cd Lab5
python3 -m venv venv && source venv/bin/activate
pip install pylint bandit flake8

python scholarship_disbursement.py
pylint scholarship_disbursement.py > pylint_report.txt
bandit -r scholarship_disbursement.py > bandit_report.txt
flake8 scholarship_disbursement.py > flake8_report.txt
```

Tool versions used: Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1, Python 3.13.
