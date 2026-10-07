"""Tests for the Mastermind game. Run from Lab4/mastermind with:

    python3 -m unittest discover -s tests -v
"""
import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game import GameOver, LOST, Mastermind, PLAYING, QUIT, WON
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


def play(game, inputs):
    """Drive game.run() with scripted input; return (printed lines, unread inputs)."""
    queue, out = list(inputs), []

    def read(prompt):
        out.append(prompt)
        return queue.pop(0)

    game.run(read=read, write=out.append)
    return out, queue


class LifecycleTests(unittest.TestCase):
    """Task 2: win / loss / quit handling, history, guess limit, frozen state."""

    def make(self, max_turns=10):
        return Mastermind(code=list("1234"), max_turns=max_turns)

    def snapshot(self, game):
        return (game.state, game.turns, list(game.history))

    def test_new_game_is_playing(self):
        game = self.make()
        self.assertEqual((game.state, game.turns, game.history), (PLAYING, 10, []))
        self.assertFalse(game.finished)

    def test_immediate_win(self):
        game = self.make()
        out, _ = play(game, ["1234"])
        self.assertEqual(game.state, WON)
        self.assertEqual(game.turns, 9)
        self.assertEqual(game.history, [("1234", 4, 0)])
        self.assertIn("Cracked the code in 1 guess!", out)

    def test_win_after_several_guesses(self):
        game = self.make()
        out, _ = play(game, ["1111", "2143", "1243", "1234"])
        self.assertEqual(game.state, WON)
        self.assertEqual(game.turns, 6)
        self.assertEqual(game.history, [("1111", 1, 0), ("2143", 0, 4),
                                        ("1243", 2, 2), ("1234", 4, 0)])
        self.assertIn("Cracked the code in 4 guesses!", out)

    def test_win_on_final_turn_is_a_win_not_a_loss(self):
        game = self.make(max_turns=3)
        play(game, ["1111", "2222", "1234"])
        self.assertEqual(game.state, WON)
        self.assertEqual(game.turns, 0)
        self.assertEqual(len(game.history), 3)

    def test_loss_after_all_guesses_used(self):
        game = self.make(max_turns=3)
        out, _ = play(game, ["1111", "2222", "3333"])
        self.assertEqual(game.state, LOST)
        self.assertEqual(game.turns, 0)
        self.assertEqual(len(game.history), 3)
        self.assertIn("Out of turns - you lose. The code was 1234", out)

    def test_quit_ends_game_and_keeps_history(self):
        game = self.make()
        out, _ = play(game, ["1111", "q"])
        self.assertEqual(game.state, QUIT)
        self.assertEqual(game.turns, 9)
        self.assertEqual(game.history, [("1111", 1, 0)])
        self.assertIn("You quit. The code was 1234", out)

    def test_quit_is_case_insensitive_and_costs_no_turn(self):
        game = self.make()
        play(game, ["Q"])
        self.assertEqual((game.state, game.turns, game.history), (QUIT, 10, []))

    def test_guess_limit_is_enforced(self):
        game = self.make(max_turns=2)
        game.submit(list("1111"))
        game.submit(list("2222"))
        self.assertEqual(game.turns, 0)
        with self.assertRaises(GameOver):
            game.submit(list("3333"))
        self.assertEqual(len(game.history), 2)

    def test_state_frozen_after_win_loss_and_quit(self):
        for max_turns, script in [(10, ["1234"]), (2, ["1111", "2222"]), (10, ["1111", "q"])]:
            with self.subTest(script=script):
                game = self.make(max_turns=max_turns)
                play(game, script)
                before = self.snapshot(game)
                for extra in ("1234", "9999", "1111"):
                    with self.assertRaises(GameOver):
                        game.submit(list(extra))
                game.quit()
                self.assertEqual(self.snapshot(game), before)

    def test_run_reads_no_input_after_game_ends(self):
        game = self.make()
        out, unread = play(game, ["1234", "1111", "1111"])
        self.assertEqual(unread, ["1111", "1111"])
        self.assertEqual(len(game.history), 1)

    def test_history_is_intact_when_game_is_lost(self):
        game = self.make(max_turns=3)
        play(game, ["1111", "4321", "1243"])
        self.assertEqual(game.history, [("1111", 1, 0), ("4321", 0, 4), ("1243", 2, 2)])


if __name__ == "__main__":
    unittest.main()
