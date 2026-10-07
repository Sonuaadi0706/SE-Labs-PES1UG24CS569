def feedback(code, guess):

    # the code, so duplicate symbols can consume the same code occurrence.
    exact = sum(a == b for a, b in zip(code, guess))
    partial = sum(ch in code for ch in guess) - exact
    return exact, partial
