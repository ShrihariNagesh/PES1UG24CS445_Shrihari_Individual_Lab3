"""Vial Code Breaker: a small terminal game used for testing-tools practice.

A cold-storage vault is locked with a secret row of four coloured vials.
You have eight guesses to find the row. After each guess the vault tells you:

    exact    vials that are the right colour in the right position
    partial  vials that are the right colour but in the wrong position

Colours: R (red), G (green), B (blue), Y (yellow), O (orange), P (purple).
A colour can appear more than once in the secret.

Play:  python game_application.py
Test:  python -m unittest test_game_application -v
"""

import random

COLOURS = "RGBYOP"
CODE_LENGTH = 4
MAX_ATTEMPTS = 8
POINTS_PER_ATTEMPT_LEFT = 100
HINT_PENALTY = 50


class InvalidGuess(ValueError):
    """The guess is not four letters from the allowed colours."""


def normalise_guess(guess):
    """Clean up a guess and return it as an upper-case string.

    Raises InvalidGuess when the guess is the wrong length or uses a letter
    that is not a colour.
    """
    if not isinstance(guess, str):
        raise InvalidGuess("guess must be text")
    cleaned = guess.replace(" ", "").upper()
    if len(cleaned) != CODE_LENGTH:
        raise InvalidGuess(f"guess must have exactly {CODE_LENGTH} vials")
    for letter in cleaned:
        if letter not in COLOURS:
            raise InvalidGuess(f"'{letter}' is not a colour, use {COLOURS}")
    return cleaned


def evaluate_guess(secret, guess):
    """Return (exact, partial) for a guess against the secret."""
    exact = sum(1 for s, g in zip(secret, guess) if s == g)
    in_secret = sum(1 for g in guess if g in secret)
    partial = in_secret - exact
    return exact, partial


def calculate_score(attempts_used, hints_used=0, solved=True):
    """Score for a finished game.

    A win is worth 100 points for the winning guess plus 100 for every guess
    left over, minus 50 per hint. A loss scores 0. The score never goes
    below 0.
    """
    if not solved:
        return 0
    if not 1 <= attempts_used <= MAX_ATTEMPTS:
        raise ValueError("attempts_used is out of range")
    attempts_left = MAX_ATTEMPTS - attempts_used
    score = (attempts_left + 1) * POINTS_PER_ATTEMPT_LEFT - hints_used * HINT_PENALTY
    return max(score, 0)


class Game:
    """One round of Vial Code Breaker."""

    def __init__(self, secret=None, rng=None):
        rng = rng or random.Random()
        self.secret = normalise_guess(secret) if secret else "".join(
            rng.choice(COLOURS) for _ in range(CODE_LENGTH))
        self.attempts_used = 0
        self.hints_used = 0
        self.solved = False
        self.history = []

    @property
    def finished(self):
        return self.solved or self.attempts_used >= MAX_ATTEMPTS

    def guess(self, text):
        """Play one guess and return (exact, partial)."""
        if self.finished:
            raise RuntimeError("the game is over")
        cleaned = normalise_guess(text)        # an invalid guess costs nothing
        self.attempts_used += 1
        feedback = evaluate_guess(self.secret, cleaned)
        self.history.append((cleaned, feedback))
        if feedback[0] == CODE_LENGTH:
            self.solved = True
        return feedback

    def hint(self):
        """Reveal the colour in the first position (costs points)."""
        self.hints_used += 1
        return self.secret[0]

    def score(self):
        if not self.finished:
            raise RuntimeError("the game is still running")
        if not self.solved:
            return 0
        return calculate_score(self.attempts_used, self.hints_used)


def main():
    game = Game()
    print("Vial Code Breaker")
    print(f"Guess the {CODE_LENGTH} vials. Colours: {' '.join(COLOURS)}. "
          f"You have {MAX_ATTEMPTS} guesses. Type 'hint' for help.")
    while not game.finished:
        text = input(f"Guess {game.attempts_used + 1}/{MAX_ATTEMPTS}: ").strip()
        if text.lower() == "hint":
            print(f"The first vial is {game.hint()} (-{HINT_PENALTY} points)")
            continue
        try:
            exact, partial = game.guess(text)
        except InvalidGuess as err:
            print(f"  {err}")
            continue
        print(f"  exact: {exact}   partial: {partial}")
    if game.solved:
        print(f"Vault open! Score: {game.score()}")
    else:
        print(f"Out of guesses. The secret was {game.secret}. Score: 0")


if __name__ == "__main__":
    main()
