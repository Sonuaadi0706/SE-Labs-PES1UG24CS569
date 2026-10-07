# Scenario 20 — Mastermind

A terminal code-breaking game with repeated symbols and structured feedback.

## Provided files

- `main.py` — entry point.
- `game.py` — game loop and history.
- `logic.py` — exact and partial match calculation.
- `requirements.txt` — dependency declaration.

## Setup

```bash
python main.py
```

## Before changing the code

Construct codes and guesses containing repeated symbols. Reason about how many times a
single code occurrence should be allowed to contribute to feedback.

## Task 1 — Correct duplicate-aware feedback

Implement feedback so each code position can be counted at most once. Exact matches
must be resolved before partial matches.

**Done when:** repeated-symbol cases produce the correct exact and partial counts.

## Task 2 — Complete game lifecycle

Add clear win/loss handling, preserve guess history, enforce the guess limit, and
prevent state changes after the game ends.

## Task 3 — Difficulty modes

Add difficulty choices that vary code length, symbol range, and allowed guesses.
The feedback algorithm must work for all supported configurations.

## Task 4 — History and input robustness

Present a readable guess history and reject malformed guesses without consuming turns.
Feedback must correspond to one accepted guess only.

## Required testing

Test exact matches, repeated symbols, no matches, mixed exact/partial cases, every
difficulty, invalid guesses, final-turn wins, losses, and quitting.


## LLM usage

You may use an LLM during the lab. The goal is to use it as a coding assistant while
retaining responsibility for understanding and testing the result.

- Inspect the existing code before asking for changes.
- Ask for explanations when you do not understand a proposed change.
- Test generated code against the stated behaviour and edge cases.
- Keep your complete LLM chat history for submission.
- Do not replace the whole project with an unrelated implementation.
- Keep all state in memory; do not add CSV, JSON, SQLite, or other persistence.

## Submission checklist

- [ ] Task 1 completed and the original defect was reproduced and fixed.
- [ ] Tasks 2–4 completed and tested.
- [ ] Boundary and invalid-input cases tested.
- [ ] No unnecessary external dependencies added.
- [ ] No persistent storage added.
- [ ] Code remains understandable and modular.
- [ ] Complete LLM chat-history link included.

## Folder structure

```text
scenario-08-mastermind/
├── README.md
├── requirements.txt
├── main.py
├── game.py
└── logic.py
```

## Submission Checklist

Submission is only the following three things:

- [ ] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [ ] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [ ] The Chat/LLM used page link, with the complete chat history
