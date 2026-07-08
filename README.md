# claude-qa-skills

**Claude Code skills that turn an AI agent into a meticulous QA engineer.**

> Your AI says "everything works, tests are green." Did it actually check?
>
> This pack makes the agent play by QA rules: every Pass/Fail verdict must be backed by an actually observed artifact (a screenshot, a network response, a log). Didn't check — it says "Not tested" instead of guessing.

🇷🇺 [Русская версия](README.ru.md) — the skills ship in two languages.

![Claude Code finds a hidden payload bug with the testing skill](assets/demo.gif)

*A real run against [`demo/`](demo/): the UI shows success and the server returns 200 — but the actual POST payload carries `"topic":"[object Object]"`. UI-only checks pass; payload inspection fails it. The recording is a time-compressed replay of an unedited session; reproduce it yourself with `node demo/server.mjs` and the prompt above.*

## What's inside

| Skill | What it does |
|---|---|
| [`testing`](skills/testing/SKILL.md) | The flagship. A universal testing framework (frontend + backend): evidence discipline, test-design techniques down to exact boundaries (BVA / EP / decision tables / state transitions / pairwise), ~1000 lines of reference checklists, multi-agent fan-out for large runs |
| [`test-review`](skills/test-review/SKILL.md) | Playwright test review before commit: severity (Blocker→Nit), line-level findings, ready-to-apply fixes `❌ before → ✅ after`, a catalog of 30+ rules with links to the official docs |
| [`test-cases`](skills/test-cases/SKILL.md) | Test-case generation by QA best practices: atomic steps, expected results taken from requirements (not from the implementation), CSV for Zephyr Scale import (Option 1) or direct creation via your TMS MCP |
| [`interview`](skills/interview/SKILL.md) | Structured requirements elicitation when the task is described "in words": 2-3 rounds of questions → a document with AC and edge cases |
| [`bug-report`](skills/bug-report/SKILL.md) | A Jira bug in a minute: data collection → preview → creation after confirmation, with your project's required custom fields |

## Why it works

**1. Evidence instead of hallucinations.** The core of the pack is discipline: a verdict only from an observed artifact; `Not tested` and `Blocked` are honest statuses, not something to hide; a review finding must point to an actually read line or linter output. This treats the main disease of AI agents in testing — confident reports about things never checked.

**2. Checklists seniors get paid for.** The `testing` references are useful even without Claude — as plain checklists:
- [`frontend.md`](skills/testing/references/frontend.md) — inputs and masks, every state of every element (hover/focus/disabled/loading), Figma comparison, design tokens, responsive layout, cross-browser
- [`backend.md`](skills/testing/references/backend.md) — HTTP semantics, contracts, idempotency, DB (transactions, concurrency, migrations), AuthN/AuthZ/IDOR, queues/DLQ/webhooks, OWASP API Top 10
- [`cross-cutting.md`](skills/testing/references/cross-cutting.md) — network mocks, UI↔Backend consistency, sessions, TZ/i18n, payments, files, search
- [`common-misses.md`](skills/testing/references/common-misses.md) — 28 checks that get missed most often
- [`fan-out.md`](skills/testing/references/fan-out.md) — how to split a large run across parallel subagents without losing evidence discipline
- [`artifacts.md`](skills/testing/references/artifacts.md) — evidence, bug-report structure, severity vs priority, run summary report

**3. The skills chain into a pipeline.** `interview` (requirements) → `test-cases` (test cases) → `testing` (the run) → `bug-report` (defects) → `test-review` (automated tests before commit).

## Install

Requires [Claude Code](https://claude.com/claude-code). Skills install by copying:

```bash
git clone https://github.com/<owner>/claude-qa-skills.git
cp -r claude-qa-skills/skills/* ~/.claude/skills/          # for all projects
# or into a specific project:
cp -r claude-qa-skills/skills/* <project>/.claude/skills/
```

Russian versions live in [`ru/skills/`](ru/skills/) — copy from there instead if you want the skills in Russian.

Claude picks the skills up automatically based on your request, or invoke them explicitly: "test this form with the testing skill", `/test-review`, `/bug-report`.

## Adapting to your project

The pack works out of the box, but gets stronger with tuning:

- **`test-review`** — fill in section K (your repository's rules: custom fixtures, suite patterns, environments). A template with examples is already inside.
- **`bug-report`** — section 0: project, issue type, your Jira's required custom fields.
- **`test-cases`** — your TMS folder-tree boundary (section 13) if the TMS project is shared across teams.
- Target resolutions and browsers — tune to your traffic analytics (defaults in `skills/testing/references/frontend.md` §2.3).

## Limitations

- `bug-report` targets Jira via the [Atlassian MCP](https://github.com/sooperset/mcp-atlassian); `test-cases` can produce CSV without any MCP.
- Accessibility (a11y/WCAG) is deliberately out of scope; hover/focus/disabled states are covered.
- The pack targets web (desktop + mobile responsive); mobile-native is on the roadmap as a checklist.

## Roadmap

- [ ] Claude Code plugin format (one-command install)
- [ ] GraphQL API checklist
- [ ] Mobile-native checklist

PRs and issues welcome. If a skill produced a verdict without proof — that's a bug, file an issue.

## License

[MIT](LICENSE)
