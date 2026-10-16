# Lab 5 — Reflection

**Student:** PES1UG24CS569 · **File analysed:** `scholarship_disbursement.py`

## 1. Which issues were the easiest to fix, and which were the hardest?

The easiest were the mechanical ones. `scheme == None` became `scheme is None`, `bySchemeCount` became `by_scheme_count`, docstrings were added, and the long lines were wrapped. Each needed one small edit and the tool told me exactly where to look. Most of Flake8's output and a large part of Pylint's fell into this group.

The hardest was removing the `global disbursed_total`. It looks like a one-word warning, but the variable was part of how the program worked. I had to decide where the total should live instead. I made the database the single source of truth and computed the total with a `SUM` query, which also meant changing `main()`. The SQL injection fix was conceptually the most important, but the change itself was small once I understood placeholders. Choosing what to do about the `try/except/pass` and the `os.system` call needed judgement about what the code was really for.

## 2. Did the tools report any false positives?

Not clearly, but one finding was low-risk in practice. Bandit flagged `os.system("echo archiving awards")` (B605 and B607). The command is a constant string with no user input, so it could not be exploited as written, and Bandit itself says it "seems safe". I still fixed it, because the pattern becomes dangerous the moment someone adds a variable to that string, and `print` does the same job.

The tools also disagreed with each other on line length: Pylint allows 100 characters and Flake8 allows 79. That is a configuration difference rather than a false positive, but it meant a line could pass one tool and fail the other. The tools also missed two real problems I found by reading the code: an award could be disbursed twice, and `main()` ran on import. Static analysis is a strong first pass but does not replace reading the code.

## 3. How would you integrate static analysis into your real development workflow?

Locally, I would run Flake8 and Pylint in the editor so that problems show up as I type, and add a pre-commit hook that runs Flake8 and Bandit before every commit, so style and security slips never enter the history. Slower or noisier checks, like a full Pylint pass, can run on demand.

In a team, I would run all three tools in continuous integration on every pull request and make the build fail on Bandit findings of medium severity or above and on a Pylint score below an agreed threshold. That makes the standard the same for everyone and removes the need for reviewers to point out style or known-unsafe patterns, leaving them free to review design and logic. Rules would be tuned in a shared config file (for example `.flake8` and `.pylintrc`), and any `# nosec` or `# pylint: disable` would need a short written reason.

## 4. What tangible improvements did you observe in code quality, readability and robustness?

The scores moved from Pylint 5.00 to 10.00, Bandit from 4 issues to 0, and Flake8 from 6 violations to 0, while the program's output stayed identical (`50000 None`, `1 50000`, `archiving awards`).

The more important changes are behavioural. User-supplied text can no longer alter the SQL, so the injection risk is gone. Errors are no longer silently swallowed. The audit list is no longer shared between calls. The running total can no longer drift out of step with the database, and an award can no longer be paid out twice. Readability improved as well: every function has a docstring that states what it returns, names follow PEP 8, `disburse()` has one clear contract (the amount, or `None`), and importing the module no longer triggers the demo, which makes the code easier to test.
