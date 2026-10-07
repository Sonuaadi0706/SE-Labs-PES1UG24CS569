"""Tests for the Mastermind game. Run from Lab4/mastermind with:

    python3 -m unittest discover -s tests -v
"""
import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logic import feedback


def fb(code, guess):
    return feedback(list(code), list(guess))


class FeedbackTests(unittest.TestCase):
    """Task 1: duplicate-aware feedback."""

    def test_original_defect_case(self):
        # Originally reported (2, 2): both 4s in the code were already used.
        self.assertEqual(fb("4413", "4444"), (2, 0))

    def test_all_exact(self):
        self.assertEqual(fb("1234", "1234"), (4, 0))
        self.assertEqual(fb("4413", "4413"), (4, 0))
        self.assertEqual(fb("1111", "1111"), (4, 0))

    def test_no_matches(self):
        self.assertEqual(fb("1111", "2222"), (0, 0))
        self.assertEqual(fb("1234", "5656"), (0, 0))

    def test_all_partial(self):
        self.assertEqual(fb("1234", "4321"), (0, 4))

    def test_mixed_exact_and_partial(self):
        self.assertEqual(fb("1234", "1325"), (1, 2))
        self.assertEqual(fb("1234", "1243"), (2, 2))

    def test_repeated_symbols_in_guess_only(self):
        self.assertEqual(fb("1234", "1115"), (1, 0))
        self.assertEqual(fb("4413", "1111"), (1, 0))
        self.assertEqual(fb("1234", "2111"), (0, 2))

    def test_repeated_symbols_in_code_only(self):
        self.assertEqual(fb("1123", "1234"), (1, 2))
        self.assertEqual(fb("1123", "3211"), (0, 4))

    def test_repeated_symbols_in_both(self):
        self.assertEqual(fb("1122", "2211"), (0, 4))
        self.assertEqual(fb("1122", "1212"), (2, 2))
        self.assertEqual(fb("1122", "1221"), (2, 2))
        self.assertEqual(fb("3331", "3133"), (2, 2))
        self.assertEqual(fb("1111", "1122"), (2, 0))
        self.assertEqual(fb("5252", "2525"), (0, 4))

    def test_exact_resolved_before_partial(self):
        # The leading 1 in the guess must not steal the code's only 1,
        # which is matched exactly by the guess's last position.
        self.assertEqual(fb("2221", "1111"), (1, 0))
        self.assertEqual(fb("1222", "2221"), (2, 2))

    def test_longer_codes(self):
        self.assertEqual(fb("123456", "654321"), (0, 6))
        self.assertEqual(fb("112233", "121212"), (2, 2))
        self.assertEqual(fb("11223344", "44332211"), (0, 8))

    def test_matches_independent_reference_exhaustively(self):
        """Compare against the textbook formula over every 4-symbol code/guess
        from a 3-symbol alphabet (6,561 pairs, heavy on repeated symbols)."""
        for code in itertools.product("123", repeat=4):
            for guess in itertools.product("123", repeat=4):
                exact = sum(c == g for c, g in zip(code, guess))
                shared = sum(min(code.count(s), guess.count(s)) for s in "123")
                with self.subTest(code=code, guess=guess):
                    self.assertEqual(feedback(list(code), list(guess)),
                                     (exact, shared - exact))


if __name__ == "__main__":
    unittest.main()
