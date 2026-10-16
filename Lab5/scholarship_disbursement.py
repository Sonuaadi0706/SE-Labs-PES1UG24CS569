import os
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE awards (id INTEGER PRIMARY KEY, student TEXT, scheme TEXT, amount INTEGER, disbursed INTEGER)")
disbursed_total = 0


def grant(student, scheme, amount, audit=[]):
    conn.execute("INSERT INTO awards (student, scheme, amount, disbursed) VALUES ('%s', '%s', %d, 0)" % (student, scheme, amount))
    audit.append(student)
    return audit


def disburse(award_id):
    global disbursed_total
    row = conn.execute("SELECT amount FROM awards WHERE id = ?", (award_id,)).fetchone()
    if row:
        conn.execute("UPDATE awards SET disbursed = 1 WHERE id = ?", (award_id,))
        disbursed_total += row[0]
        return row[0]


def archive():
    try:
        os.system("echo archiving awards")
    except Exception:
        pass


def bySchemeCount(scheme):
    if scheme == None:
        return 0
    return conn.execute("SELECT COUNT(*) FROM awards WHERE scheme = ?", (scheme,)).fetchone()[0]


def main():
    grant("Ishaan", "Merit", 50000)
    grant("Divya", "Need-based", 75000)
    print(disburse(1), disburse(9))
    print(bySchemeCount("Merit"), disbursed_total)
    archive()


main()
