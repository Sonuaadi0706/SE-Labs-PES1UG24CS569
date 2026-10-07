import random
from dataclasses import dataclass
from logic import InvalidGuess, feedback, validate_guess

PLAYING, WON, LOST, QUIT = "playing", "won", "lost", "quit"
QUIT_WORDS = ("q", "quit")


class GameOver(Exception):
    """Raised when a guess is submitted after the game has already ended."""


@dataclass(frozen=True)
class Difficulty:
    name: str
    length: int      # positions in the secret code
    symbols: int     # code symbols are the digits 1..symbols
    max_turns: int   # guesses allowed

    @property
    def alphabet(self):
        return "".join(str(n) for n in range(1, self.symbols + 1))

    def describe(self):
        return f"{self.length} digits from 1-{self.symbols}, {self.max_turns} guesses"


EASY = Difficulty("easy", 3, 4, 12)
MEDIUM = Difficulty("medium", 4, 6, 10)   # the original game
HARD = Difficulty("hard", 5, 8, 8)
DIFFICULTIES = (EASY, MEDIUM, HARD)


def choose_difficulty(read=input, write=print):
    """Ask for a difficulty by number or name; return None if the player quits."""
    write("Choose a difficulty:")
    for number, level in enumerate(DIFFICULTIES, 1):
        write(f"  {number}) {level.name:<6} - {level.describe()}")
    while True:
        try:
            choice = read("Difficulty (number or name, q to quit) > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            write("")
            return None
        if choice in QUIT_WORDS:
            return None
        for number, level in enumerate(DIFFICULTIES, 1):
            if choice in (str(number), level.name):
                return level
        write(f"Please choose 1-{len(DIFFICULTIES)} or a difficulty name.")


class Mastermind:
    def __init__(self, difficulty=MEDIUM, code=None):
        self.difficulty = difficulty
        self.code = code or [str(random.randint(1, difficulty.symbols))
                             for _ in range(difficulty.length)]
        self.history = []
        self.turns = difficulty.max_turns
        self.state = PLAYING

    @property
    def finished(self):
        return self.state != PLAYING

    def submit(self, guess):
        """Score one accepted guess and advance the game; return (exact, partial).

        `guess` is a string (or sequence) of symbols. Raises GameOver once the
        game has ended and InvalidGuess for a malformed guess; in both cases all
        state is left untouched, so no turn is spent and no feedback is produced.
        """
        if self.finished:
            raise GameOver(f"The game is already over ({self.state}).")
        symbols = validate_guess("".join(guess), self.difficulty.length, self.difficulty.alphabet)
        exact, partial = feedback(self.code, symbols)
        self.history.append(("".join(symbols), exact, partial))
        self.turns -= 1
        if exact == len(self.code):
            self.state = WON
        elif self.turns == 0:
            self.state = LOST
        return exact, partial

    def quit(self):
        if not self.finished:
            self.state = QUIT

    def history_lines(self):
        """The guess history as a table, one row per accepted guess."""
        width = max(5, 2 * self.difficulty.length - 1)
        lines = [f"{'#':>3}  {'Guess':<{width}}  {'Exact':>5}  {'Partial':>7}"]
        for number, (guess, exact, partial) in enumerate(self.history, 1):
            lines.append(f"{number:>3}  {' '.join(guess):<{width}}  {exact:>5}  {partial:>7}")
        return lines

    def run(self, read=input, write=print):
        level = self.difficulty
        write(f"Mastermind ({level.name}) — enter {level.length} digits "
              f"from 1 to {level.symbols}, or q to quit.")
        while not self.finished:
            try:
                raw = read(f"{self.turns} turns left > ").strip()
            except (EOFError, KeyboardInterrupt):
                write("")
                raw = "q"
            if raw.lower() in QUIT_WORDS:
                self.quit()
                break
            try:
                self.submit(raw)
            except InvalidGuess as problem:
                write(str(problem))
                continue
            for line in self.history_lines():
                write(line)
        self.announce_result(write)

    def announce_result(self, write=print):
        code = "".join(self.code)
        guesses = len(self.history)
        if self.state == WON:
            write(f"Cracked the code in {guesses} guess{'es' if guesses != 1 else ''}!")
        elif self.state == LOST:
            write(f"Out of turns - you lose. The code was {code}")
        elif self.state == QUIT:
            write(f"You quit. The code was {code}")
