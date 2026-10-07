from collections import Counter


class InvalidGuess(ValueError):
    """A guess that is malformed; its message is suitable to show the player."""


def validate_guess(raw, length, alphabet):
    """Return the guess as a list of symbols, or raise InvalidGuess.

    A guess must have exactly `length` characters, all drawn from `alphabet`.
    Membership is checked against the alphabet itself (not str.isdigit), so
    look-alike characters such as full-width or Arabic-Indic digits are rejected.
    """
    if not raw:
        raise InvalidGuess("Enter a guess, or q to quit.")
    if len(raw) != length:
        raise InvalidGuess(f"A guess needs exactly {length} digits - you entered {len(raw)}.")
    bad = sorted({ch for ch in raw if ch not in alphabet})
    if bad:
        shown = " ".join(repr(ch) for ch in bad)
        raise InvalidGuess(f"Only digits {alphabet[0]} to {alphabet[-1]} are allowed - not {shown}.")
    return list(raw)


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
