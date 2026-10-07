from collections import Counter


def feedback(code, guess):
    """Return (exact, partial) for a guess against the secret code.

    Each code position is counted at most once:
      1. Exact matches (same symbol, same position) are resolved first.
      2. Positions that were not exact matches are then paired up by symbol,
         so a code occurrence already used by an exact match - or by an
         earlier partial match - can never contribute again.
    """
    exact = sum(c == g for c, g in zip(code, guess))
    unmatched_code = Counter(c for c, g in zip(code, guess) if c != g)
    unmatched_guess = Counter(g for c, g in zip(code, guess) if c != g)
    partial = sum((unmatched_code & unmatched_guess).values())
    return exact, partial
