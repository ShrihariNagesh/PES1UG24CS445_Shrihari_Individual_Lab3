# Vibe Coding Bug Fix Guide and Retest Report

**Game:** Vial Code Breaker (`game_application.py`) | **AI assistant used:** Claude

"Vibe coding" here means: run the tests, hand the failure to an AI assistant in plain language,
review the fix it proposes, apply it, and run the tests again.

## Step 1: Run the tests (before the fix)

```bash
python -m unittest test_game_application -v
```

Output:

```text
test_1_guess_validation (test_game_application.VialCodeBreakerTests.test_1_guess_validation)
Bad guesses are rejected and do not use up an attempt. ... ok
test_2_feedback_without_repeated_colours (test_game_application.VialCodeBreakerTests.test_2_feedback_without_repeated_colours)
Exact and partial counts when every colour appears once. ... ok
test_3_score_and_attempt_limit (test_game_application.VialCodeBreakerTests.test_3_score_and_attempt_limit)
Score rules, and the game stops after the last attempt. ... ok
test_4_feedback_with_repeated_colours (test_game_application.VialCodeBreakerTests.test_4_feedback_with_repeated_colours)
A colour is never counted more times than it appears in the secret. ... FAIL

======================================================================
FAIL: test_4_feedback_with_repeated_colours (test_game_application.VialCodeBreakerTests.test_4_feedback_with_repeated_colours)
A colour is never counted more times than it appears in the secret.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_game_application.py", line 53, in test_4_feedback_with_repeated_colours
    self.assertEqual(evaluate_guess("RGBY", "RRRR"), (1, 0))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Tuples differ: (1, 3) != (1, 0)

First differing element 1:
3
0

- (1, 3)
?     ^

+ (1, 0)
?     ^


----------------------------------------------------------------------
Ran 4 tests in 0.002s

FAILED (failures=1)
```

Three tests pass. `test_4_feedback_with_repeated_colours` fails.

### Reading the failure

- Secret `RGBY`, guess `RRRR`.
- Expected `(1, 0)`: one exact match (the first R) and nothing else.
- Got `(1, 3)`: the three extra R vials were reported as "right colour, wrong position".
- The secret has only one R, so those three cannot be partial matches.

## Step 2: Prompt for the AI assistant

Paste the failing output and the function, then ask in plain words:

> This test fails with `(1, 3) != (1, 0)` for secret `RGBY` and guess `RRRR`. Here is
> `evaluate_guess()`. Explain why the partial count is wrong when a colour repeats, and give me the
> smallest change that fixes it without changing the results of the other three tests.

Three things make this prompt work: it includes the exact failing values, it includes the code, and
it asks for the smallest change so the fix stays reviewable.

## Step 3: Diagnosis and patch

**Diagnosis.** The line

```python
in_secret = sum(1 for g in guess if g in secret)
```

walks over the guess and adds 1 for every vial whose colour exists anywhere in the secret. With the
guess `RRRR` it adds 4, even though the secret holds a single R. Subtracting the 1 exact match
leaves 3.

**Rule that should hold.** A colour can match at most as many times as it appears in both rows:
`min(count in secret, count in guess)`.

**Patch (`game_patch.diff`).**

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

**Review before applying.** For rows with no repeated colours, `min(1, 1)` is 1 per shared colour,
which is the same total the old line gave. So tests 1 to 3 cannot change. One line changed, no new
imports.

## Step 4: Retest (after the fix)

```text
test_1_guess_validation (test_game_application.VialCodeBreakerTests.test_1_guess_validation)
Bad guesses are rejected and do not use up an attempt. ... ok
test_2_feedback_without_repeated_colours (test_game_application.VialCodeBreakerTests.test_2_feedback_without_repeated_colours)
Exact and partial counts when every colour appears once. ... ok
test_3_score_and_attempt_limit (test_game_application.VialCodeBreakerTests.test_3_score_and_attempt_limit)
Score rules, and the game stops after the last attempt. ... ok
test_4_feedback_with_repeated_colours (test_game_application.VialCodeBreakerTests.test_4_feedback_with_repeated_colours)
A colour is never counted more times than it appears in the secret. ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
```

All four tests pass, and the three tests that passed before still pass (no regression).

## Summary

| Item | Value |
|---|---|
| Failing test | `test_4_feedback_with_repeated_colours` |
| Defect | Partial matches over-counted when a colour repeats |
| Function | `evaluate_guess()` |
| Lines changed | 1 |
| Before | 3 of 4 tests pass |
| After | 4 of 4 tests pass |
