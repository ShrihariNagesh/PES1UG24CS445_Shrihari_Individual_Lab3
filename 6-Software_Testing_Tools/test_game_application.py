"""The four unit tests for Vial Code Breaker.

Run:  python -m unittest test_game_application -v
"""

import unittest

from game_application import (
    Game, InvalidGuess, MAX_ATTEMPTS, calculate_score, evaluate_guess,
    normalise_guess,
)


class VialCodeBreakerTests(unittest.TestCase):

    def test_1_guess_validation(self):
        """Bad guesses are rejected and do not use up an attempt."""
        self.assertEqual(normalise_guess(" r g b y "), "RGBY")
        for bad in ("RGB", "RGBYO", "RGBX", "", 1234):
            with self.assertRaises(InvalidGuess):
                normalise_guess(bad)
        game = Game(secret="RGBY")
        with self.assertRaises(InvalidGuess):
            game.guess("ZZZZ")
        self.assertEqual(game.attempts_used, 0)

    def test_2_feedback_without_repeated_colours(self):
        """Exact and partial counts when every colour appears once."""
        self.assertEqual(evaluate_guess("RGBY", "RGBY"), (4, 0))
        self.assertEqual(evaluate_guess("RGBY", "YBGR"), (0, 4))
        self.assertEqual(evaluate_guess("RGBY", "RBGO"), (1, 2))
        self.assertEqual(evaluate_guess("RGBY", "OPOP"), (0, 0))

    def test_3_score_and_attempt_limit(self):
        """Score rules, and the game stops after the last attempt."""
        self.assertEqual(calculate_score(1), 800)
        self.assertEqual(calculate_score(MAX_ATTEMPTS), 100)
        self.assertEqual(calculate_score(3, hints_used=2), 500)
        self.assertEqual(calculate_score(MAX_ATTEMPTS, hints_used=5), 0)
        self.assertEqual(calculate_score(4, solved=False), 0)

        game = Game(secret="RGBY")
        for _ in range(MAX_ATTEMPTS):
            game.guess("OOOO")
        self.assertTrue(game.finished)
        self.assertFalse(game.solved)
        self.assertEqual(game.score(), 0)
        with self.assertRaises(RuntimeError):
            game.guess("RGBY")

    def test_4_feedback_with_repeated_colours(self):
        """A colour is never counted more times than it appears in the secret."""
        self.assertEqual(evaluate_guess("RGBY", "RRRR"), (1, 0))
        self.assertEqual(evaluate_guess("RRGB", "RGRR"), (1, 2))
        self.assertEqual(evaluate_guess("RRGG", "GGRR"), (0, 4))
        self.assertEqual(evaluate_guess("RGGB", "GGGG"), (2, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
