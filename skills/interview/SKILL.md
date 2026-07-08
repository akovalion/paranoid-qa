---
name: interview
description: Structured requirements gathering through a series of questions. Use when the task is described verbally/informally (not from an issue tracker ticket) and scope, AC, and edge cases need clarifying before work starts.
allowed-tools:
  — AskUserQuestion
  — Write
---

# Interview: requirements gathering through questions

Help the user turn an informal task description into complete requirements ready to hand off to the `test-cases` or `testing` skills.

## When to apply
- The task is described verbally or in general terms, without a ticket
- No AC, no mockups, no clear scope
- The user is unsure what exactly to test/automate

If the task already comes from an issue tracker (Jira etc.) with a full description — this skill is not needed: gather context straight from the ticket (via the tracker's MCP: description, comments, attachments, linked issues) and hand off to `test-cases`.

## Process

**Round 1: scope and context.** Ask 3-4 questions via `AskUserQuestion`:
- What exactly is being checked (feature, page, element)
- Where it lives (URL, screen, navigation path)
- Task type (new functionality / regression / bug)
- Platforms (desktop / mobile / both)

**Round 2: behavior and AC.** Based on the round 1 answers:
- Happy path — what behavior counts as correct
- Edge cases — which negative scenarios matter
- UI states (loading, error, empty, disabled) — if applicable
- Integrations — any APIs / external services

**Round 3: clarifications on remaining gaps.** Only if critical gaps remain after rounds 1-2. Group related questions.

Maximum 3 rounds. If the requirements are still incomplete — log the gaps as "Questions for the analyst/PM" and work with what you have.

## Output format

Once the interview is done, assemble a structured summary:

```markdown
# Requirements: <short task name>

## Context
- Type: <new feature / regression / bug>
- Platforms: <desktop / mobile / both>
- URL / location: <…>

## Scope
<what exactly is being checked, briefly>

## Acceptance Criteria
- <AC 1>
- <AC 2>

## Scenarios
**Happy path:** <description>

**Edge cases:**
- <case 1>
- <case 2>

## Integrations
<APIs, external services — if any>

## Open questions for the analyst/PM
- <question 1>
```

Save the summary to an md file (e.g. `requirements_<task_name>.md` in the current working directory) and offer to hand it off to `test-cases` or `testing`.

## What to prefer
- 4 precise questions beat 10 boilerplate ones
- Tie questions to the previous round's answers instead of running down a checklist
- If the user answers "don't know" — log it as a question for the analyst, do not push
- Use concrete answer options in questions (AskUserQuestion options), not open-ended wording
