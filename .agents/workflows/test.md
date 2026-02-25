---
description: Runs project tests to ensure logic coverage and prevent regressions. Use this workflow before proposing any commits.
---

# Testing Workflow

This workflow must be executed to verify that the code works correctly and no regressions have been introduced.

1. **Run all tests**
   // turbo
   Execute the full test suite using pytest.
   `pytest tests/`

2. **Analyze results**
   If all tests pass successfully, you may proceed to the next step.
   If there are failures:

- Analyze the error output to understand the root cause.
- Fix the code that caused the failure.
- Return to step 1 and re-run all tests. Repeat until all tests pass.

3. **Check test coverage (Highly Recommended)**
   // turbo
   Verify that the code coverage is adequate, especially for newly added features.
   `pytest --cov=src tests/`
