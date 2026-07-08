## 7. Fan-out: parallel run

Split the meticulous run across **control axes** instead of a single linear pass. Each axis is driven by a separate subagent (`Agent`) with fresh context and one narrow task — more exacting than a single pass where, by the end of a long flow, attention dulls. Launched by the orchestrator (main loop) from this skill.

### 7.1 When to apply
- **Yes:** long multi-step flow (wizard, form with branching), full screen regression, prod/test comparison, release E2E, a screen with many states/elements.
- **No (linear is cheaper and sufficient):** a single simple page, quick smoke, verifying/reproducing one bug, re-running a narrow section. Fan-out costs more tokens (N agents × context) — justified by coverage, do not apply it everywhere.

### 7.2 Principle: collect sequentially, analyze in parallel
- **One browser.** MCP servers (Playwright/Chrome DevTools) are session-scoped — one browser instance per session. Subagents do NOT drive the browser in parallel: navigation/state conflicts will follow. Only the orchestrator touches the browser.
- **Boundary:** browser action and artifact collection = orchestrator (sequential); judgment on a collected artifact = subagent (parallel). Subagents receive paths to the artifact files and read them (`Read`), never call the browser.

### 7.3 Steps
1. **Collection (orchestrator, sequential).** Walk the screens/states, store artifacts in the run's working folder (`/tmp/<run>/`): screenshots `screen-N.png`, DOM and computed-style dump `dom-N.json`, network log/HAR `network.json`, extracted texts `texts.md`; for cross-browser — paired Chromium/WebKit artifacts. Capture transient and interactive states (hover/focus/disabled/loading) empirically, as the doctrine requires.
2. **Fan-out (`Agent`, parallel).** Launch the subagents in a single message (several `Agent` calls at once = parallel start), one per axis. Give each a brief (§7.5).
3. **Synthesis (orchestrator, no agent).** Collect the findings, dedup (visual and contrast often report the same gray), set/normalize severity, map to AC, filter out duplicates and non-defects.
4. **Output.** Summary defect list with proofs → bug reports (the `bug-report` skill from this pack if installed, otherwise the structure from `artifacts.md`); uncovered areas and `Blocked` — explicitly, with reasons.

### 7.4 Axes (default — customize per task)
| Axis (subagent) | What it looks for | Artifact |
|---|---|---|
| Visual + tokens | whether there is a single "black"/"gray", font, spacing, heading sizes; diff of same-type elements across screens | screenshots + computed styles |
| Texts vs mockup | missing/altered phrases, second sentences of subheadings, overflow/wrapping | `texts.md` + source of truth |
| Forms + payload | submit body for `[object Object]`/empty/malformed fields; statuses of ALL requests; BVA/negative | `network.json` + payloads |
| Element states | rest/hover/focus/active/disabled/loading of every interactive element; tap targets on mobile | screenshots + computed styles of states |
| Cross-browser | bugs visible only in WebKit or only in Chromium | paired artifacts |

The set adapts to the task: static landing page — drop "forms", add "responsive" (canonical viewports — §2.3 of `frontend.md`); pure backend — fan out across endpoints/resources instead of UI axes.

### 7.5 Subagent brief (pass to each)
- Paths to the required artifacts — only what is relevant to the axis, not the whole dump.
- Source of truth for the axis: AC/spec/mockup description; on conflict — priority (AC → spec → Figma → prod).
- Evidence doctrine: Pass/Fail only from an artifact; not sure / not visible → "not verified", not a guess.
- Strict output format (§7.6) — so synthesis stays mechanical.
- Boundary: do not call the browser, work only from files.

### 7.6 Subagent output format
A list of findings, each: `{ axis, screen/element, expected (+source), actual (+proof: screenshot path / network entry / style diff), severity, type: defect | question to requirements | not reproducible }`. Without a proof artifact a finding does not count.

### 7.7 Discipline
- Never parallelize the browser — subagents only analyze the collected artifacts.
- Evidence discipline is not lost in delegation: proof travels with every finding.
- Dedup is mandatory at synthesis, otherwise one defect arrives from 2-3 axes.
- Token cost is deliberate: the number of axes fits the task, not "always 5".
