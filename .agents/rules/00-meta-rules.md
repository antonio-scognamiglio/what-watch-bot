---
trigger: always_on
name: Meta Rules
description: Defines the protocol for creating, updating, and interacting with rules, skills, and workflows. MUST read before acting on any structural or behavioral requests.
---

# Meta Rule — How to Create and Update Rules, Skills, and Workflows

## Purpose

This is a **meta-rule**. It defines when and how to create or update project rules, workflows, and skills, and documents the core Antigravity features (Rules, Workflows, Skills, MCP). Every time a relevant change is made to the codebase, evaluate whether to codify it as a rule or a skill.

---

## Antigravity Core Features

### 1. Rules Locations & Triggers

Rules define behaviors, style, and constraints for the Agent.

- **Workspace rules**: `.agents/rules/*.md` (loaded automatically)
- **Global rules**: `~/.gemini/GEMINI.md` (loaded automatically)

Rules are plain Markdown files but support configuration via YAML frontmatter to control _when_ the AI should invoke them:

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
- `glob`: Applies the rule only when the AI interacts with files matching the glob pattern.

### 2. Workflows

Workflows are structured sequences of steps for repeatable multi-step procedures (e.g., generate tests, code review).

- **Location**: `.agents/workflows/*.md`
- **Trigger**: Manually via `/workflow-name` in the chat.
- **Behavior**: A workflow can call another workflow ("Call /workflow-2").
- Max 12,000 characters. Save as markdown.

### 3. Skills

Skills extend the agent's capabilities by integrating knowledge, scripts, and best practices for a specific task.

- **Workspace skills**: `<workspace-root>/.agents/skills/<skill-folder>/SKILL.md`
- **Global skills**: `~/.gemini/antigravity/skills/<skill-folder>/SKILL.md`

**Anatomy**: Skills are capabilities that the agent decides to use based on their description. For the technical structure (YAML frontmatter, `scripts/` folders, etc.), rely entirely on the `skill-creator` tool or consult existing skills as templates.

### 4. MCP Integration (Model Context Protocol)

MCP connects Antigravity securely to local tools, databases, and external services.

- **Purpose**: Provides real-time context without manual copy-pasting (e.g., live DB schemas, logs).
- **Custom Servers**: Configured by modifying `mcp_config.json` via the MCP store.
- **Features**: Context Resources (to fetch data) and Custom Tools (to execute safe actions).

---

## When to Create a New Rule or Skill

Create a **Rule** when:

- A pattern or convention is established that will repeat across the project
- The agent made the same mistake more than once
- A coding style or structural decision is made

Create a **Skill** when:

- You have a specific external tool or complex script execution workflow that requires instructions, scripts, and examples to guide the agent properly.

**Bootstrap Protocol (How to add capabilities):**

1. **Mandatory Global Check**: Whenever the user asks you to perform a task (e.g. brainstorming, debugging, planning, writing), you MUST proactively check `~/.agents/skills/` and `~/.gemini/antigravity/skills/` using your file reading tools to see if a relevant official skill exists. Do this BEFORE executing the task, even if you feel capable of doing it natively.
2. **Always Search First**: Before creating a custom skill, you MUST use `npx skills find <query>` (via the `find-skills` local tool) to check if an official skill exists.
3. **Install Locally**: If a relevant skill exists globally or remotely, install it locally in the project (`npx skills add <skill-name>`) so the repo remains portable and does not pollute the user's global environment.
4. **Scaffold if Missing**: If no skill exists and you MUST create a new one, do NOT create files manually. Use `npx skills init <skill-name>` (via the `skill-creator` tool).
5. **Self-Healing**: If you need `skill-creator` but it's missing, use `find-skills` to install `skill-creator` locally first, then proceed.

## When to Update an Existing Rule or Skill

- A previous convention has changed
- A better approach has been found
- The rule/skill was too vague and caused incorrect behavior

---

## Best Practices

**Keep rules short.** Under 500 lines. Split if necessary.
**Be specific, not generic.**

- ❌ `Write clean code`
- ✅ `Use guard clauses for input validation at the top of every function. Avoid nested if blocks.`

**Reference real files** instead of duplicating code in the rule.
**Avoid documenting the obvious** (e.g., how to use git or npm).
**Check rules into git.**

---

## Auto-Update Protocol

When you apply a code change that establishes or modifies a convention:

1. Check whether a related rule exists in `.agents/rules/`
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
│   ├── 00-meta-rules.md         # How to create/update rules, skills, workflows
│   └── testing.md
├── workflows/
│   ├── generate-tests.md        # /generate-tests
│   └── code-review.md           # /code-review
└── skills/
    └── my-custom-skill/
        └── SKILL.md             # Custom agent capability
```

---

## Rules vs Workflows vs Skills

| Feature      | Use when…                                                                                                                                                        |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Rule**     | A behavior, constraint, or style convention should be active (always, on model decision, or glob matching).                                                      |
| **Workflow** | A multi-step repeatable task needs to be triggered on demand via `/slash-command`.                                                                               |
| **Skill**    | A specific functionality requires detailed instructions, external scripts, or examples, and the agent should discover and use it automatically based on context. |

---

## Anti-Yes-Man Principle

- Do not automatically confirm the user's conclusions
- Read the relevant files before acting
- Propose the minimum change necessary
- If something is unclear, ask before implementing
- Never assume — verify first, then act
