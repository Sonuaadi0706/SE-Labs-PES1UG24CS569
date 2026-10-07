import random
from logic import feedback


class Mastermind:
    def __init__(self):
        self.code = [str(random.randint(1, 6)) for _ in range(4)]
        self.history = []
        self.turns = 10

    def run(self):
        print("Mastermind — enter four digits from 1 to 6.")
        while self.turns:
            raw = input(f"{self.turns} turns left > ").strip()
            if raw.lower() == "q":
                return
            if len(raw) != 4 or any(ch not in "123456" for ch in raw):
                print("Enter exactly four digits from 1 to 6.")
                continue
            guess = list(raw)
            exact, partial = feedback(self.code, guess)
            self.history.append((raw, exact, partial))
            self.turns -= 1
            print("Exact:", exact, " Partial:", partial)
            if exact == 4:
                print("Cracked the code!")
                return
        print("The code was", "".join(self.code))
