# Lab 4 — VibeCoding: Mastermind

**Course:** Software Engineering (PES University, Dept. of CSE) · **Student:** PES1UG24CS569 · **Lab:** 4 — VibeCoding

| | |
|---|---|
| Assigned repository (Scenario 20 — Mastermind) | https://github.com/SETAPESU26/20_mastermind |
| Personal submission repository | https://github.com/Sonuaadi0706/SE-Labs-PES1UG24CS569 |

## Objective

Use an LLM coding assistant (Claude) to take the assigned, deliberately broken Mastermind game,
reproduce and fix its defect, and add the four features listed in the assigned README — inspecting
the code first, testing every change, and keeping one Git commit per task.

**The defect.** `logic.feedback()` computed `partial = (guessed symbols that appear anywhere in the code) − exact`,
so one code position could be counted several times. With secret `4413` and guess `4444` it reported
`Exact 2, Partial 2`; the correct answer is `Exact 2, Partial 0` (both 4s in the code are already used
by the exact matches). It was reproduced on the untouched code before any change was made (see `before_10s.mp4`).

## Tasks completed

| Task | What was done | Where |
|---|---|---|
| **1 — Duplicate-aware feedback** | Two-pass algorithm: exact matches are resolved first; only the remaining (unmatched) positions are then paired by symbol, so each code position counts at most once. | `mastermind/logic.py` |
| **2 — Complete game lifecycle** | Explicit state (`playing` / `won` / `lost` / `quit`); `Mastermind.submit()` scores and records one guess, enforces the guess limit, and raises `GameOver` leaving all state untouched after the game ends; win / loss / quit messages; history preserved in every outcome. | `mastermind/game.py` |
| **3 — Difficulty modes** | `Difficulty` config + start-up menu: **easy** 3 digits from 1–4, 12 guesses · **medium** 4 digits from 1–6, 10 guesses (the original game) · **hard** 5 digits from 1–8, 8 guesses. Code generation, validation, prompts and the guess limit all read from the chosen mode. | `mastermind/game.py`, `mastermind/main.py` |
| **4 — History and input robustness** | `validate_guess()` / `InvalidGuess` reject empty, wrong-length, out-of-range and look-alike (full-width / Arabic-Indic) digits with a specific message; validation happens before any state change, so a bad guess never spends a turn, enters the history, or produces feedback. A history table is shown after every accepted guess; `q`/`quit`, Ctrl-D and Ctrl-C quit cleanly. | `mastermind/logic.py`, `mastermind/game.py` |

## Testing

A standard-library `unittest` suite (**53 tests**, no third-party packages) lives in
[`mastermind/tests/test_mastermind.py`](mastermind/tests/test_mastermind.py).

```bash
cd Lab4/mastermind
python3 -m unittest discover -s tests -v
```

Result of the final run: `Ran 53 tests … OK`. Run against the original `logic.py`, the Task 1 feedback tests fail
(3,628 failing sub-tests), confirming they detect the defect.

| Required case | Covered by (test class → test) |
|---|---|
| Exact matches | `FeedbackTests` → `test_all_exact` |
| Repeated symbols (guess only / code only / both) | `FeedbackTests` → `test_repeated_symbols_in_*`, `test_original_defect_case` |
| No matches | `FeedbackTests` → `test_no_matches` |
| Mixed exact + partial | `FeedbackTests` → `test_mixed_exact_and_partial`, `test_exact_resolved_before_partial` |
| Independent check of the algorithm | `FeedbackTests` → `test_matches_independent_reference_exhaustively` (6,561 code/guess pairs vs. a counting formula) |
| Every difficulty | `DifficultyTests` → distinct config, valid generated codes, validation, guess limit, win/loss and duplicate-aware feedback in **each** mode, menu |
| Invalid / malformed guesses | `ValidationTests` → 16 malformed inputs (empty, blank, short, long, letters, 0, out of range, spaces, punctuation, sign, decimal, tab, full-width and Arabic-Indic digits, newline) |
| Invalid guesses spend no turn, add no history, give no feedback | `ValidationTests` → `test_submit_rejects_malformed_guess_without_changing_state`, `test_invalid_input_in_run_spends_no_turn_and_prints_no_feedback`, `test_prompt_turn_counter_does_not_move_on_invalid_input` |
| Valid guess recorded / counted / answered exactly once | `ValidationTests` → `test_valid_guess_is_recorded_and_counted_exactly_once`, `test_each_accepted_guess_produces_exactly_one_new_history_row` |
| First-turn win | `LifecycleTests` → `test_immediate_win` |
| Last-turn (final-guess) win | `LifecycleTests` → `test_win_on_final_turn_is_a_win_not_a_loss`; `DifficultyTests` → `test_win_and_loss_in_every_mode` |
| Loss on the final allowed guess | `LifecycleTests` → `test_loss_after_all_guesses_used`; `DifficultyTests` → `test_guess_limit_matches_the_mode` |
| Invalid input right before a winning guess / on the final turn | `ValidationTests` → `test_invalid_input_before_winning_guess`, `test_invalid_input_on_final_turn_does_not_end_the_game` |
| Multiple / repeated invalid inputs | `ValidationTests` → `test_invalid_input_in_run_spends_no_turn_and_prints_no_feedback` |
| Quitting | `LifecycleTests` → `test_quit_*`; `ValidationTests` → `test_quit_words`, `test_end_of_input_and_ctrl_c_quit_cleanly` |
| State / history unchanged after the game ends | `LifecycleTests` → `test_state_frozen_after_win_loss_and_quit`, `test_run_reads_no_input_after_game_ends`, `test_history_is_intact_when_game_is_lost`; `ValidationTests` → `test_game_over_takes_precedence_over_validation` |
| Readable history | `ValidationTests` → `test_history_table_is_readable`, `test_history_table_is_empty_before_first_guess_and_scales_with_length` |

## Deliverables

| Deliverable | File |
|---|---|
| Video **before** (10 s, original code, bug visible) | [`evidence/before_10s.mp4`](evidence/before_10s.mp4) |
| Video **after** (10 s, final game) | [`evidence/after_10s.mp4`](evidence/after_10s.mp4) |
| Complete LLM chat history (PDF) | [`evidence/LLM_Chat_History.pdf`](evidence/LLM_Chat_History.pdf) |
| LLM chat link | [`evidence/LLM_Chat_Link.txt`](evidence/LLM_Chat_Link.txt) |
| Updated source code | [`mastermind/`](mastermind/) |

**How the videos were made.** Both are real screen recordings (macOS `screencapture`, window-only, ~10 s, H.264 MP4) of the actual game
running in a Terminal window. To make them repeatable, a small helper script (not part of the submission) launched the game with
`random.seed(0)` — which gives the secret `4413` — through `runpy`, without modifying any game source, and typed the guesses with
human-like timing. The secret and the expected results are printed above the game by the helper for the viewer's benefit; the game's own
output is unmodified.

## Running the game

```bash
cd Lab4/mastermind
python3 main.py
```

Standard library only (the project's recommended Python is 3.9+; it was developed and tested here with Python 3.14).

## Constraints verified

- **No unnecessary external dependencies** — only the Python standard library (`random`, `collections`, `dataclasses`; `unittest` for tests). `requirements.txt` is unchanged.
- **No persistence** — no files, CSV, JSON, SQLite or database are read or written; all game state lives in memory.
- **Original project structure and concept retained** — same four files (`main.py`, `game.py`, `logic.py`, `requirements.txt`), still a terminal Mastermind; the assigned `README.md` text is preserved with a Lab 4 section appended.
- Labs 1–3 are untouched; all Lab 4 work is inside `Lab4/`.
- Nothing was pushed to, and no pull request was opened against, `SETAPESU26/20_mastermind`.

## Git commits

| # | Commit | Message |
|---|---|---|
| 1 | `33abfde` | Lab 4: Add Mastermind baseline |
| 2 | `3b1a33a` | Lab 4: Fix duplicate-aware feedback — **Task 1** |
| 3 | `a770f86` | Lab 4: Complete game lifecycle — **Task 2** |
| 4 | `0d6561f` | Lab 4: Add difficulty modes — **Task 3** |
| 5 | `ccb9632` | Lab 4: Harden input and history — **Task 4** |
| 6 | see `git log` | Lab 4: Add submission evidence and documentation |

## LLM usage

Claude (Claude Code, `claude-sonnet-5-5`) was used as the coding assistant, working autonomously from one detailed lab prompt that set out the
workflow: inspect the code, reproduce the defect, record the "before" video, then implement, test and commit Tasks 1–4 one at a time, record the
"after" video, and package the evidence. The complete conversation — prompt, Claude's replies, every command run and its output — is in
[`evidence/LLM_Chat_History.pdf`](evidence/LLM_Chat_History.pdf). The PDF was produced from the session's exported transcript; screenshots appear as
placeholders and the last few packaging/push steps happen after the export, so they are not in it (see the note in
[`evidence/LLM_Chat_Link.txt`](evidence/LLM_Chat_Link.txt)).
