---
trigger: always_on
---

# Testing Execution Pipeline Rules

- **Test-Driven Requirements**: Whenever you add a new feature, update logic, or fix a bug, you MUST create or update the corresponding tests in the `tests/` directory.
- **Follow Testing Patterns**: You MUST read and follow the installed skill at `.agents/skills/python-testing-patterns/SKILL.md` for writing tests.
- **Isolation Rules**: You MUST use `pytest` as the testing framework and `pytest-mock` to completely isolate external dependencies. Do not make real network requests in tests.
- **Validation Check**: You MUST verify that your code works by running the `/test` workflow and ensuring all tests pass BEFORE proposing a commit.
