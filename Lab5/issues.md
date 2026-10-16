# Lab 5 — Issue Table

**File analysed:** `scholarship_disbursement.py` (assigned repo `SETAPESU26/L5_20_scholarship_disbursement`)
**Tools:** Pylint 4.1.3 · Bandit 1.9.4 · Flake8 7.4.1

Line numbers refer to the **original** file (`reports/before/`). Rows are ordered by severity: security and bug-risk first, style last.
The "Fixed in" column points to the commit that resolved the row.

| Issue | Type | Line(s) | Description | Fix Approach | Fixed in |
|-------|------|---------|-------------|--------------|----------|
| SQL injection via string formatting (Bandit **B608**, Medium; CWE-89) | Security | 10 | `grant()` built its `INSERT` with `"... VALUES ('%s', '%s', %d, 0)" % (...)`. A student name such as `x'); DROP TABLE awards;--` would be executed as SQL. | Use `?` placeholders and pass `(student, scheme, amount)` as parameters so values are always bound as data. Verified with a hostile name: the table survives and the name is stored verbatim. | Commit 1 (Bandit) |
| Mutable default argument (Pylint **W0102**) | Bug | 9 | `grant(..., audit=[])` — the default list is created once and shared by every call, so audit entries leak between unrelated calls. | Default is now `audit=None`; a new list is created inside the function when none is passed. | Commit 2 (Pylint) |
| Global mutable state (Pylint **W0603**, **C0103**) | Maintainability | 6, 16 | `disbursed_total` was a module-level variable modified via `global`, and was not UPPER_CASE as Pylint expects for a constant. State kept outside the database can drift from it. | Removed the global. New `disbursed_total()` computes `SUM(amount)` over rows where `disbursed = 1`, so the database is the single source of truth. | Commit 2 (Pylint) |
| Inconsistent return statements (Pylint **R1710**) | Bug | 15–21 | `disburse()` returned a value on one path and silently fell off the end (implicit `None`) on the other. | Return `None` explicitly when the award is not found, and document it in the docstring. | Commit 2 (Pylint) |
| Overly broad exception (Pylint **W0718**) + try/except/pass (Bandit **B110**, Low) | Bug / Security | 25–28 | `except Exception: pass` swallowed every error, so a failed archive step would go completely unnoticed. | Removed the `try/except/pass`. The only statement inside it no longer needs protection, and genuine errors now surface instead of being hidden. | Commit 1 (Bandit) |
| Process started with a shell / partial path (Bandit **B605**, **B607**, Low; CWE-78) | Security | 26 | `os.system("echo archiving awards")` spawns a shell and relies on `echo` being found on `PATH`. The string is constant here, but the pattern is a command-injection risk if it is ever changed to include input. | Replaced with `print("archiving awards")`; the shell call and the unused `import os` are gone. | Commit 1 (Bandit) |
| `== None` comparison (Pylint **C0121**, Flake8 **E711**) | Style | 32 | `scheme == None` compares by equality; `None` is a singleton and should be tested with identity. | Changed to `scheme is None`. | Commit 2 (Pylint) |
| Function name not snake_case (Pylint **C0103**) | Style | 31 | `bySchemeCount` is camelCase, against PEP 8. | Renamed to `by_scheme_count` and updated the call in `main()`. | Commit 2 (Pylint) |
| String formatted with `%` (Pylint **C0209**) | Style | 10 | The SQL string used old-style `%` formatting. | Superseded by the parameterised query above, so no formatted string remains. | Commit 1 (Bandit) |
| Missing module / function docstrings (Pylint **C0114**, **C0116** ×5) | Style | 1, 9, 15, 24, 31, 37 | The module and all five functions had no docstring. | Added a module docstring and a docstring on every function describing purpose, parameters and return value. | Commit 2 (Pylint) |
| Lines too long (Pylint **C0301**; Flake8 **E501** ×5) | Style | 5, 10, 17, 19, 34 | Five lines exceeded Flake8's 79-character limit; two (5 and 10) also exceeded Pylint's 100. | Wrapped the `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE` and `COUNT` statements across lines. | Commit 2 (Pylint) for >100, Commit 3 (Flake8) for the rest |

## Found by reading the code (not reported by the tools)

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| An award could be disbursed more than once | Bug | 15–21 | `disburse()` never checked the `disbursed` flag, so calling it twice for the same award paid it twice and added it to the running total twice. | The lookup now only matches rows with `disbursed = 0`; a repeat call returns `None` and changes nothing. |
| `main()` ran on import | Maintainability | 45 | The bare `main()` call at module level executed the demo whenever the file was imported. | Wrapped in `if __name__ == "__main__":`. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.00 / 10 (16 messages) | **10.00 / 10** (0 messages) |
| Bandit | 4 issues (1 Medium, 3 Low) | **0 issues** |
| Flake8 | 6 violations | **0 violations** |

Program output is identical before and after (`50000 None` / `1 50000` / `archiving awards`). Full reports are in `reports/before/` and `reports/after/`.
