# paranoid-qa

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
| [`testing`](skills/testing/SKILL.md) | The flagship. A universal testing framework (frontend + backend): evidence discipline, test-design techniques down to exact boundaries (BVA / EP / decision tables / state transitions / pairwise), nearly 1,000 individual checks in the reference files, multi-agent fan-out for large runs |
| [`test-review`](skills/test-review/SKILL.md) | Playwright test review before commit: severity (Blocker→Nit), line-level findings, ready-to-apply fixes `❌ before → ✅ after`, a catalog of 40+ rules with links to the official docs |
| [`test-cases`](skills/test-cases/SKILL.md) | Test-case generation by QA best practices: atomic steps, expected results taken from requirements (not from the implementation), CSV for Zephyr Scale import (Option 1) or direct creation via your TMS MCP |
| [`interview`](skills/interview/SKILL.md) | Structured requirements elicitation when the task is described "in words": 2-3 rounds of questions → a document with AC and edge cases |
| [`bug-report`](skills/bug-report/SKILL.md) | A Jira bug in a minute: data collection → preview → creation after confirmation, with your project's required custom fields |

## Why it works

**1. Evidence instead of hallucinations.** The core of the pack is discipline: a verdict only from an observed artifact; `Not tested` and `Blocked` are honest statuses, not something to hide; a review finding must point to an actually read line or linter output. This treats the main disease of AI agents in testing — confident reports about things never checked.

**2. Checklists seniors get paid for.** The `testing` references are useful even without Claude — as plain checklists:
- [`frontend.md`](skills/testing/references/frontend.md) — inputs and masks, every state of every element (hover/focus/disabled/loading), Figma comparison, design tokens, responsive layout, cross-browser
- [`backend.md`](skills/testing/references/backend.md) — HTTP semantics, contracts, idempotency, DB (transactions, concurrency, migrations), AuthN/AuthZ/IDOR, queues/DLQ/webhooks, OWASP API Top 10
- [`cross-cutting.md`](skills/testing/references/cross-cutting.md) — network mocks, UI↔Backend consistency, sessions, TZ/i18n, payments, files, search
- [`common-misses.md`](skills/testing/references/common-misses.md) — 26 checks that get missed most often
- [`fan-out.md`](skills/testing/references/fan-out.md) — how to split a large run across parallel subagents without losing evidence discipline, including parallel test-case execution with a separate browser per agent (§7.8)
- [`artifacts.md`](skills/testing/references/artifacts.md) — evidence, bug-report structure, severity vs priority, run summary report

**3. The skills chain into a pipeline.** `interview` (requirements) → `test-cases` (test cases) → `testing` (the run) → `bug-report` (defects) → `test-review` (automated tests before commit).

## Install

Requires [Claude Code](https://claude.com/claude-code).

**As a plugin — one command, versioned updates (recommended):**

```
/plugin marketplace add akovalion/paranoid-qa
/plugin install paranoid-qa@paranoid-qa        # English skills
/plugin install paranoid-qa-ru@paranoid-qa     # Russian skills
```

**Or by copying — if you want to edit the skills as your own:**

```bash
git clone https://github.com/akovalion/paranoid-qa.git
cp -r paranoid-qa/skills/* ~/.claude/skills/          # for all projects
# or into a specific project:
cp -r paranoid-qa/skills/* <project>/.claude/skills/
```

Russian versions live in [`ru/skills/`](ru/skills/) — copy from there instead if you want the skills in Russian.

Claude picks the skills up automatically based on your request, or invoke them explicitly: "test this form with the testing skill". Slash form: `/test-review` for the copied install, `/paranoid-qa:test-review` for the plugin install.

## MCP servers

The skills use whatever tools your Claude Code session has. For the full experience:

- [Playwright MCP](https://github.com/microsoft/playwright-mcp) — required for UI runs of the `testing` skill: drives the browser, captures network payloads. The README demo needs it. Defaults to Chromium; for the cross-browser checks the skills call for, add a second instance with `--browser webkit` (Safari engine) — and `--device "iPhone 15"` covers mobile emulation.
- [Atlassian MCP](https://github.com/sooperset/mcp-atlassian) — used by `bug-report` (creates Jira issues) and for pulling ticket context into `test-cases`.
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) — optional addition: console, performance traces.
- [Figma MCP](https://github.com/GLips/Figma-Context-MCP) — used by `test-cases` and `testing` to work from mockups. Look at the mockup **visually, not only its structure**: pull the node tree (`get_figma_data`) AND download the rendered frames (`download_figma_images`, desktop + mobile) — part of the content hides in component templates and breakpoint differences show only in the picture. For mockup-heavy work a Figma **Dev (or Full) seat** is recommended — higher export limits.
- A TMS MCP (e.g. a Zephyr Scale community server) — optional, only for creating test cases directly; CSV export works without it.

Not an MCP, but a strong companion: [Playwright CLI](https://github.com/microsoft/playwright-cli) (`playwright-cli`) — the `testing` skill leans on it for scripted repeatable flows (the page-map helpers) and for parallel execution with a separate browser process per agent (`fan-out.md` §7.8); it takes `--browser webkit` too.

No MCP is needed for backend/API checks (the agent uses curl from the shell), CSV export, or reading the checklists.

## Adapting to your project

The pack works out of the box, but gets stronger with tuning:

- **`test-review`** — fill in section K (your repository's rules: custom fixtures, suite patterns, environments). A template with examples is already inside.
- **`bug-report`** — section 0: project, issue type, your Jira's required custom fields.
- **`test-cases`** — your TMS folder-tree boundary (section 13) if the TMS project is shared across teams.
- Target resolutions and browsers — tune to your traffic analytics (defaults in `skills/testing/references/frontend.md` §2.3).

## Limitations

- `bug-report` is Jira-only for now (via the Atlassian MCP, see above).
- Accessibility (a11y/WCAG) is deliberately out of scope; hover/focus/disabled states are covered.
- The pack targets web (desktop + mobile responsive); mobile-native is on the roadmap as a checklist.

## Hooks: the enforcement layer (opt-in)

Skills convince the agent to stay disciplined; [`examples/hooks`](examples/hooks) makes the critical rules impossible to skip: `git commit` is denied without a fresh green test run, editing a spec injects a run reminder, and the agent cannot finish a turn with dirty tests. Copy-paste install, never auto-enabled by the plugin. Design notes (deny-when-in-doubt asymmetry, loop fuse) are in the folder README.

## Roadmap

- [x] Claude Code plugin format (one-command install)
- [x] Enforcement hooks: commit/stop gates, test-edit tracker ([examples/hooks](examples/hooks))
- [ ] GraphQL API checklist
- [ ] Mobile-native checklist

PRs and issues welcome. If a skill produced a verdict without proof — that's a bug, file an issue.

## License

[MIT](LICENSE)
