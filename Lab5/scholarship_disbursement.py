"""Scholarship disbursement ledger.

Grants awards under different schemes, disburses the funds, archives
records and counts awards per scheme.
"""
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE awards (id INTEGER PRIMARY KEY, student TEXT, "
    "scheme TEXT, amount INTEGER, disbursed INTEGER)"
)


def grant(student, scheme, amount, audit=None):
    """Record a new, not yet disbursed award and log the student's name.

    ``audit`` is an optional list that collects the names of students granted
    awards; a fresh list is created per call when none is given.
    """
    if audit is None:
        audit = []
    conn.execute(
        "INSERT INTO awards (student, scheme, amount, disbursed) "
        "VALUES (?, ?, ?, 0)",
        (student, scheme, amount),
    )
    audit.append(student)
    return audit


def disburse(award_id):
    """Mark an award as disbursed and return its amount.

    Returns None when the award does not exist or was already disbursed.
    """
    row = conn.execute(
        "SELECT amount FROM awards WHERE id = ? AND disbursed = 0", (award_id,)
    ).fetchone()
    if row is None:
        return None
    conn.execute("UPDATE awards SET disbursed = 1 WHERE id = ?", (award_id,))
    return row[0]


def disbursed_total():
    """Return the total amount disbursed so far."""
    return conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM awards WHERE disbursed = 1"
    ).fetchone()[0]


def archive():
    """Announce that the awards are being archived."""
    print("archiving awards")


def by_scheme_count(scheme):
    """Return how many awards were granted under the given scheme."""
    if scheme is None:
        return 0
    return conn.execute(
        "SELECT COUNT(*) FROM awards WHERE scheme = ?", (scheme,)
    ).fetchone()[0]


def main():
    """Run a short demonstration of the ledger."""
    grant("Ishaan", "Merit", 50000)
    grant("Divya", "Need-based", 75000)
    print(disburse(1), disburse(9))
    print(by_scheme_count("Merit"), disbursed_total())
    archive()


if __name__ == "__main__":
    main()
