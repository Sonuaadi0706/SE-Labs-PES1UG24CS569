import random
from logic import feedback

PLAYING, WON, LOST, QUIT = "playing", "won", "lost", "quit"


class GameOver(Exception):
    """Raised when a guess is submitted after the game has already ended."""


class Mastermind:
    def __init__(self, code=None, max_turns=10):
        self.code = code or [str(random.randint(1, 6)) for _ in range(4)]
        self.history = []
        self.turns = max_turns
        self.state = PLAYING

    @property
    def finished(self):
        return self.state != PLAYING

    def submit(self, guess):
        """Score one accepted guess and advance the game; return (exact, partial).

        Raises GameOver, leaving all state untouched, once the game has ended.
        """
        if self.finished:
            raise GameOver(f"The game is already over ({self.state}).")
        exact, partial = feedback(self.code, guess)
        self.history.append(("".join(guess), exact, partial))
        self.turns -= 1
        if exact == len(self.code):
            self.state = WON
        elif self.turns == 0:
            self.state = LOST
        return exact, partial

    def quit(self):
        if not self.finished:
            self.state = QUIT

    def run(self, read=input, write=print):
        write("Mastermind — enter four digits from 1 to 6.")
        while not self.finished:
            raw = read(f"{self.turns} turns left > ").strip()
            if raw.lower() == "q":
                self.quit()
                break
            if len(raw) != 4 or any(ch not in "123456" for ch in raw):
                write("Enter exactly four digits from 1 to 6.")
                continue
            exact, partial = self.submit(list(raw))
            write(f"Exact: {exact}  Partial: {partial}")
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
