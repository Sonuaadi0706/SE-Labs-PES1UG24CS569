"""Tests for the Mastermind game. Run from Lab4/mastermind with:

    python3 -m unittest discover -s tests -v
"""
import itertools
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game import (DIFFICULTIES, EASY, HARD, LOST, MEDIUM, PLAYING, QUIT, WON,
                  Difficulty, GameOver, Mastermind, choose_difficulty)
from logic import InvalidGuess, feedback, validate_guess


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
        level = Difficulty("test", 4, 6, max_turns)
        return Mastermind(level, code=list("1234"))

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


def run_menu(inputs):
    queue, out = list(inputs), []
    level = choose_difficulty(read=lambda prompt: queue.pop(0), write=out.append)
    return level, out


class DifficultyTests(unittest.TestCase):
    """Task 3: difficulty modes vary length, symbol range and guess limit."""

    def test_modes_differ_in_every_setting(self):
        for attr in ("length", "symbols", "max_turns"):
            values = [getattr(level, attr) for level in DIFFICULTIES]
            self.assertEqual(len(set(values)), len(values), attr)

    def test_medium_is_the_original_game(self):
        self.assertEqual((MEDIUM.length, MEDIUM.symbols, MEDIUM.max_turns), (4, 6, 10))

    def test_default_game_is_medium(self):
        self.assertIs(Mastermind().difficulty, MEDIUM)

    def test_generated_codes_are_valid_for_every_mode(self):
        for level in DIFFICULTIES:
            for seed in range(200):
                random.seed(seed)
                game = Mastermind(level)
                with self.subTest(level=level.name, seed=seed):
                    self.assertEqual(len(game.code), level.length)
                    self.assertTrue(all(c in level.alphabet for c in game.code))
                    self.assertEqual(game.turns, level.max_turns)

    def test_codes_can_contain_repeated_symbols(self):
        for level in DIFFICULTIES:
            repeated = False
            for seed in range(200):
                random.seed(seed)
                code = Mastermind(level).code
                repeated = repeated or len(set(code)) < len(code)
            self.assertTrue(repeated, level.name)

    def test_seed_zero_still_gives_the_original_code(self):
        random.seed(0)
        self.assertEqual("".join(Mastermind(MEDIUM).code), "4413")

    def test_guess_validation_follows_the_mode(self):
        cases = [
            (EASY, "123", True), (EASY, "1234", False), (EASY, "12", False), (EASY, "125", False),
            (MEDIUM, "1236", True), (MEDIUM, "123", False), (MEDIUM, "12345", False), (MEDIUM, "1237", False),
            (HARD, "12348", True), (HARD, "1234", False), (HARD, "123456", False), (HARD, "12349", False),
        ]
        for level, guess, valid in cases:
            with self.subTest(level=level.name, guess=guess):
                game = Mastermind(level, code=list("1" * level.length))
                play(game, [guess, "q"])
                self.assertEqual(len(game.history), 1 if valid else 0)

    def test_guess_limit_matches_the_mode(self):
        for level in DIFFICULTIES:
            with self.subTest(level=level.name):
                wrong = "2" * level.length
                game = Mastermind(level, code=list("1" * level.length))
                for _ in range(level.max_turns - 1):
                    game.submit(list(wrong))
                self.assertEqual(game.state, PLAYING)
                game.submit(list(wrong))
                self.assertEqual((game.state, game.turns), (LOST, 0))
                self.assertEqual(len(game.history), level.max_turns)

    def test_win_and_loss_in_every_mode(self):
        for level in DIFFICULTIES:
            code = list(level.alphabet[: level.length])
            wrong = "".join(reversed(code)) if level.length > 1 else "9"
            with self.subTest(level=level.name, outcome="win-on-last-turn"):
                game = Mastermind(level, code=code)
                play(game, [wrong] * (level.max_turns - 1) + ["".join(code)])
                self.assertEqual((game.state, game.turns), (WON, 0))
            with self.subTest(level=level.name, outcome="loss"):
                game = Mastermind(level, code=code)
                play(game, [wrong] * level.max_turns)
                self.assertEqual((game.state, game.turns), (LOST, 0))

    def test_duplicate_aware_feedback_in_every_mode(self):
        cases = [
            (EASY, "113", "111", (2, 0)),
            (EASY, "121", "211", (1, 2)),
            (MEDIUM, "4413", "4444", (2, 0)),
            (MEDIUM, "1122", "2211", (0, 4)),
            (HARD, "11223", "12121", (2, 2)),
            (HARD, "88123", "18812", (1, 3)),
            (HARD, "88123", "88888", (2, 0)),
        ]
        for level, code, guess, expected in cases:
            with self.subTest(level=level.name, code=code, guess=guess):
                game = Mastermind(level, code=list(code))
                self.assertEqual(game.submit(list(guess)), expected)

    def test_menu_accepts_number_or_name(self):
        for choice, expected in [("1", EASY), ("2", MEDIUM), ("3", HARD),
                                 ("easy", EASY), (" Medium ", MEDIUM), ("HARD", HARD)]:
            with self.subTest(choice=choice):
                self.assertIs(run_menu([choice])[0], expected)

    def test_menu_reprompts_on_bad_choice_and_can_quit(self):
        level, out = run_menu(["", "9", "extreme", "3"])
        self.assertIs(level, HARD)
        self.assertEqual(sum("Please choose" in line for line in out), 3)
        self.assertIsNone(run_menu(["q"])[0])

    def test_menu_lists_every_mode(self):
        out = run_menu(["q"])[1]
        for level in DIFFICULTIES:
            self.assertTrue(any(level.name in line and level.describe() in line for line in out))


MALFORMED = [
    ("", "empty"), ("   ", "blank"), ("123", "too short"), ("12345", "too long"),
    ("12a4", "letter"), ("abcd", "all letters"), ("1204", "zero"), ("1274", "above range"),
    ("12 3", "inner space"), ("1,23", "comma"), ("-123", "sign"), ("1.23", "decimal"),
    ("12\t3", "tab"), ("１２３４", "full-width digits"), ("١٢٣٤", "Arabic-Indic digits"),
    ("1234\n", "newline"),
]


class ValidationTests(unittest.TestCase):
    """Task 4: malformed guesses are rejected and never touch the game state."""

    def make(self, max_turns=10):
        return Mastermind(Difficulty("test", 4, 6, max_turns), code=list("1234"))

    def snapshot(self, game):
        return (game.state, game.turns, list(game.history))

    def test_validate_guess_accepts_well_formed_guesses(self):
        self.assertEqual(validate_guess("1234", 4, "123456"), list("1234"))
        self.assertEqual(validate_guess("6666", 4, "123456"), list("6666"))
        self.assertEqual(validate_guess("88888", 5, "12345678"), list("88888"))

    def test_validate_guess_rejects_malformed_guesses(self):
        for raw, why in MALFORMED:
            with self.subTest(why):
                with self.assertRaises(InvalidGuess):
                    validate_guess(raw, 4, "123456")

    def test_error_messages_say_what_is_wrong(self):
        for raw, expected in [("", "Enter a guess"), ("123", "exactly 4 digits - you entered 3"),
                              ("12a4", "'a'"), ("1274", "'7'")]:
            with self.subTest(raw=raw):
                with self.assertRaises(InvalidGuess) as caught:
                    validate_guess(raw, 4, "123456")
                self.assertIn(expected, str(caught.exception))

    def test_submit_rejects_malformed_guess_without_changing_state(self):
        for raw, why in MALFORMED:
            with self.subTest(why):
                game = self.make()
                game.submit("1111")
                before = self.snapshot(game)
                with self.assertRaises(InvalidGuess):
                    game.submit(raw)
                self.assertEqual(self.snapshot(game), before)

    def test_invalid_input_in_run_spends_no_turn_and_prints_no_feedback(self):
        game = self.make()
        # run() trims input first, so a trailing newline is not malformed there.
        inputs = [raw for raw, why in MALFORMED if why != "newline"]
        out, unread = play(game, inputs + ["q"])
        self.assertEqual(unread, [])
        self.assertEqual((game.state, game.turns, game.history), (QUIT, 10, []))
        self.assertFalse([line for line in out if "Exact" in line])
        self.assertEqual(sum(line.startswith("A guess needs") or line.startswith("Only digits")
                             or line.startswith("Enter a guess") for line in out), len(inputs))

    def test_prompt_turn_counter_does_not_move_on_invalid_input(self):
        game = self.make()
        out, _ = play(game, ["12", "abcd", "", "q"])
        prompts = [line for line in out if line.endswith("turns left > ")]
        self.assertEqual(prompts, ["10 turns left > "] * 4)

    def test_valid_guess_is_recorded_and_counted_exactly_once(self):
        game = self.make()
        play(game, ["1111", "q"])
        self.assertEqual(game.history, [("1111", 1, 0)])
        self.assertEqual(game.turns, 9)

    def test_each_accepted_guess_produces_exactly_one_new_history_row(self):
        game = self.make()
        out, _ = play(game, ["1111", "oops", "2222", "12", "3333", "q"])
        tables = [i for i, line in enumerate(out) if line.lstrip().startswith("#")]
        self.assertEqual(len(tables), 3)                      # one table per accepted guess
        self.assertEqual(len(game.history), 3)
        self.assertEqual(game.turns, 7)

    def test_invalid_input_before_winning_guess(self):
        game = self.make()
        play(game, ["12", "9999", "", "1234"])
        self.assertEqual(game.state, WON)
        self.assertEqual(game.history, [("1234", 4, 0)])
        self.assertEqual(game.turns, 9)

    def test_invalid_input_on_final_turn_does_not_end_the_game(self):
        game = self.make(max_turns=1)
        play(game, ["bad", "99", "1234"])
        self.assertEqual((game.state, game.turns), (WON, 0))
        game = self.make(max_turns=1)
        out, _ = play(game, ["bad", "1111"])
        self.assertEqual((game.state, game.turns), (LOST, 0))

    def test_game_over_takes_precedence_over_validation(self):
        game = self.make()
        play(game, ["1234"])
        before = self.snapshot(game)
        for raw in ("9999", "", "1111"):
            with self.assertRaises(GameOver):
                game.submit(raw)
        self.assertEqual(self.snapshot(game), before)

    def test_input_is_trimmed_but_not_otherwise_altered(self):
        game = self.make()
        play(game, ["  1111  ", "q"])
        self.assertEqual(game.history, [("1111", 1, 0)])

    def test_quit_words(self):
        for word in ("q", "Q", "quit", "QUIT", " q "):
            with self.subTest(word=word):
                game = self.make()
                play(game, ["1111", word])
                self.assertEqual((game.state, game.turns, len(game.history)), (QUIT, 9, 1))

    def test_end_of_input_and_ctrl_c_quit_cleanly(self):
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error.__name__):
                game, out = self.make(), []
                feed = iter(["1111"])

                def read(prompt):
                    try:
                        return next(feed)
                    except StopIteration:
                        raise error

                game.run(read=read, write=out.append)
                self.assertEqual((game.state, game.turns, len(game.history)), (QUIT, 9, 1))

    def test_menu_end_of_input_returns_none(self):
        def read(prompt):
            raise EOFError

        self.assertIsNone(choose_difficulty(read=read, write=lambda line: None))

    def test_history_table_is_readable(self):
        game = self.make()
        game.submit("3144")
        game.submit("1243")
        game.submit("1234")
        self.assertEqual(game.history_lines(), [
            "  #  Guess    Exact  Partial",
            "  1  3 1 4 4      1        2",
            "  2  1 2 4 3      2        2",
            "  3  1 2 3 4      4        0",
        ])

    def test_history_table_is_empty_before_first_guess_and_scales_with_length(self):
        game = self.make()
        self.assertEqual(game.history_lines(), ["  #  Guess    Exact  Partial"])
        hard = Mastermind(HARD, code=list("12345"))
        hard.submit("54321")
        header, row = hard.history_lines()
        self.assertEqual(len(header), len(row))
        self.assertIn("5 4 3 2 1", row)

    def test_validation_follows_each_difficulty(self):
        for level in DIFFICULTIES:
            game = Mastermind(level)
            with self.subTest(level=level.name):
                for raw in ("", "1" * (level.length - 1), "1" * (level.length + 1),
                            "1" * (level.length - 1) + str(level.symbols + 1)):
                    with self.assertRaises(InvalidGuess):
                        game.submit(raw)
                self.assertEqual((game.turns, game.history), (level.max_turns, []))
                game.submit(level.alphabet[-1] * level.length)
                self.assertEqual((game.turns, len(game.history)), (level.max_turns - 1, 1))


if __name__ == "__main__":
    unittest.main()
