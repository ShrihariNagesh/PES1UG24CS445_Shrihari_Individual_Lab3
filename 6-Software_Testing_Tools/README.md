# 6. Software Testing Tools Practice

**Problem Statement #17** | Shrihari Nagesh | PES1UG24CS445

A small game, four automated unit tests, one real failing test, the fix, and the retest.

## Files

| File | What it is |
|---|---|
| `game_application.py` | The game (fixed version) |
| `test_game_application.py` | Exactly 4 unit tests (`unittest`, no extra installs) |
| `game_patch.diff` | The one-line fix as a diff |
| `vibe_coding_bugfix_guide.md` | Step-by-step record: failing run, AI prompt, diagnosis, patch, retest |

## What the game does

**Vial Code Breaker** is a terminal code-breaking game. A vault is locked with a secret row of four
coloured vials (R, G, B, Y, O, P; a colour may repeat). The player has 8 guesses. After each guess
the game answers with two numbers:

- **exact**: right colour in the right position
- **partial**: right colour in the wrong position

A win scores 100 points for the winning guess plus 100 for every guess left over, minus 50 per hint.

```bash
python game_application.py
```

## How to test

```bash
cd 6-Software_Testing_Tools
python -m unittest test_game_application -v
```

| # | Test | What it checks |
|---|---|---|
| 1 | `test_1_guess_validation` | Wrong length or unknown colour is rejected and costs no attempt |
| 2 | `test_2_feedback_without_repeated_colours` | Exact and partial counts when each colour appears once |
| 3 | `test_3_score_and_attempt_limit` | Score rules and the 8-guess limit |
| 4 | `test_4_feedback_with_repeated_colours` | A colour is never counted more often than it appears in the secret |

## The bug and how it was fixed

Test 4 failed on the first version:

```text
AssertionError: Tuples differ: (1, 3) != (1, 0)
```

For the secret `RGBY` and the guess `RRRR`, the game reported 3 partial matches. There is only one
red vial in the secret and it is already an exact match, so the right answer is 0.

**Cause:** `evaluate_guess()` counted every guessed vial whose colour exists anywhere in the secret,
so a repeated colour was counted once per repeat.

**Fix:** count each colour at most as many times as it appears in both rows.

```diff
diff --git a/6-Software_Testing_Tools/game_application.py b/6-Software_Testing_Tools/game_application.py
index 76b2bd6..971dfd2 100644
--- a/6-Software_Testing_Tools/game_application.py
+++ b/6-Software_Testing_Tools/game_application.py
@@ -46,7 +46,7 @@ def normalise_guess(guess):
 def evaluate_guess(secret, guess):
     """Return (exact, partial) for a guess against the secret."""
     exact = sum(1 for s, g in zip(secret, guess) if s == g)
-    in_secret = sum(1 for g in guess if g in secret)
+    in_secret = sum(min(secret.count(c), guess.count(c)) for c in set(guess))
     partial = in_secret - exact
     return exact, partial
```

The failing output and the function were given to an AI coding assistant (Claude), which diagnosed
the over-count and proposed this one-line change. Full steps are in
[`vibe_coding_bugfix_guide.md`](./vibe_coding_bugfix_guide.md).

## Results before and after

| Test | Before patch | After patch |
|---|:---:|:---:|
| `test_1_guess_validation` | PASS | PASS |
| `test_2_feedback_without_repeated_colours` | PASS | PASS |
| `test_3_score_and_attempt_limit` | PASS | PASS |
| `test_4_feedback_with_repeated_colours` | **FAIL** | PASS |
| **Total** | 3 / 4 | 4 / 4 |

Both versions are in the commit history: the failing version is commit `6e9ba9f`, and the next
commit applies the patch.

**Repository after the fix:** https://github.com/ShrihariNagesh/LAB-3_Activity_ShrihariNagesh_PES1UG24CS445
