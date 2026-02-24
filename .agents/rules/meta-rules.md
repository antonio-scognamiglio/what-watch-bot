# Meta Rule — How to Create and Update Rules

## Purpose

This is a **meta-rule**. It defines when and how to create or update project rules. Every time a relevant change is made to the codebase, evaluate whether to codify it as a rule.

---

## Antigravity Rule Locations

| Scope                   | Location                 | Loaded                          |
| ----------------------- | ------------------------ | ------------------------------- |
| **Workspace rules**     | `.agents/rules/*.md`     | Automatically, always           |
| **Workspace workflows** | `.agents/workflows/*.md` | On demand via `/workflow-name`  |
| **Global rule**         | `~/.gemini/GEMINI.md`    | Automatically, in every project |

| **Global rule** | `~/.gemini/GEMINI.md` | Automatically, in every project |

Rules in `.agents/rules/` are plain Markdown files. **However, they support configuration via YAML frontmatter** to control _when_ the AI should invoke them. Use one file per concern.

### Rule Frontmatter (Triggers)

You can configure a rule's activation behavior using YAML frontmatter at the top of the file:

```yaml
---
trigger: always_on | manual | model_decision
glob: "*.py" # (optional, applies to specific files)
description: "Brief rule intent"
---
```

- `always_on`: Loaded in every context automatically.
- `manual`: Only triggered if explicitly mentioned/requested by the user.
- `model_decision`: Loaded if the AI's internal model deems it relevant based on the `description`.
- `glob`: Applies the rule only when the AI interacts with files matching the glob pattern (e.g., `*.test.ts`, `src/api/*`).

Workflows in `.agents/workflows/` are triggered manually via `/` in the chat. Use them for repeatable multi-step procedures, not persistent behavior rules.

---

## When to Create a New Rule

Create a rule when:

- A pattern or convention is established that will repeat across the project
- The agent made the same mistake more than once and the fix can be stated explicitly
- A library, internal API, or architectural pattern is introduced for the first time
- A coding style or structural decision is made (naming, error handling, file organization)

> **Start simple.** Add rules only when you notice the agent making the same mistake repeatedly. Do not over-optimize before you understand your patterns.

---

## When to Update an Existing Rule

- A previous convention has changed
- A better approach has been found
- The rule was too vague and caused incorrect behavior

---

## Best Practices

**Keep rules under 500 lines.** If a rule is growing large, split it into multiple focused files.

**Be specific, not generic.**

- ❌ `Write clean code`
- ✅ `Use guard clauses for input validation at the top of every function. Avoid nested if blocks.`

**Reference real files instead of copying content.** Point to canonical examples in the codebase rather than duplicating code in the rule. This keeps rules short and prevents them from going stale.

**Avoid documenting the obvious.** The agent already knows common tools (npm, git, pytest) and common style conventions. Only add rules for patterns specific to this project.

**Do not copy entire style guides.** Use a linter instead.

**Check rules into git.** The whole team benefits. When the agent makes a mistake, update the rule immediately.

---

## Auto-Update Protocol

When you apply a code change that establishes or modifies a convention:

1. Check whether a related rule already exists in `.agents/rules/`
2. If yes — update it
3. If no — create a new focused `.md` file in `.agents/rules/`
4. Communicate which rule was created or changed and why

Output format after a change:

```text
✅ Change applied.
📌 Rule updated: .agents/rules/error-handling.md
   Reason: added pattern "use early return for input validation"
```

---

## Recommended File Structure

```text
.agents/
├── rules/
│   ├── core.md                  # Universal standards, always active
│   ├── error-handling.md
│   ├── naming-conventions.md
│   ├── api-patterns.md
│   └── testing.md
└── workflows/
    ├── generate-tests.md        # /generate-tests
    └── code-review.md           # /code-review
```

For global preferences that apply across all projects, add them to `~/.gemini/GEMINI.md`.

---

## Rules vs Workflows

| Use a **rule** when…                   | Use a **workflow** when…                         |
| -------------------------------------- | ------------------------------------------------ |
| Behavior should always be active       | The procedure is triggered on demand             |
| It is a constraint or style convention | It is a multi-step repeatable task               |
| Example: "always add docstrings"       | Example: `/generate-tests` after code is written |

---

## Anti-Yes-Man Principle

- Do not automatically confirm the user's conclusions
- Read the relevant files before acting
- Propose the minimum change necessary
- If something is unclear, ask before implementing
- Never assume — verify first, then act
