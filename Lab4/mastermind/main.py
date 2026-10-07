from game import Mastermind, choose_difficulty

if __name__ == "__main__":
    level = choose_difficulty()
    if level:
        Mastermind(level).run()
