---
name: testing
description: Universal testing framework (frontend + backend) — a meticulous run of any testing task with evidence discipline. Use when you need to test a feature/form/build/API/service, draft a test plan, run checks, perform exploratory or regression testing, or find defects.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
---

Master checklist "how to test anything" — frontend/UI and backend/services. Doctrine:
- **Meticulousness by default.** Cover everything yourself: happy path → negative → boundaries → rare combinations. Depth scales with risk, but never skip check classes.
- **Evidence discipline.** Pass/Fail is set ONLY from an observed artifact (screenshot, network response, log, DB dump). Didn't check — `Not tested`; couldn't — `Blocked` with a reason. No hallucinations and no "should work by logic".
- **Log every deviation immediately.** Record any mismatch with the design (Figma)/requirements at once, even a minor one (spacing, copy, color).
- **The goal is to replace manual testing.** Reliability over speed; "ran out of time / couldn't" is stated plainly.

---

## 0. Process (for any task)

**Context gathering**
- Read the ticket in full: description, AC/Gherkin, comments, attachments, linked issues (blocks/relates/epic), component, release.
- Pin the source of truth for each requirement (AC → spec/Confluence → Figma → production behavior) and the precedence on conflict.
- Check Figma: version, mode (desktop/mobile/adaptive), states (default/hover/focus/active/disabled/loading/error/empty), component variants, tokens; what is in the design vs what is "implied".
- Find existing test cases (in your TMS — Zephyr/TestRail/other) and autotests (in the project's autotest repository): reuse, identify gaps, don't duplicate.
- Capture a production/preprod baseline (how the feature works now — for regression and reproducing bugs on the current version).
- Clarify the environment: environment instance, access, test accounts/roles, feature flags, data state, build version/commit.
- Identify integrations and dependencies: external APIs, payment providers, auth, queues — what is mocked, what is real.
- Explicitly record out of scope (native apps, unsupported browsers, legacy flows).

**Requirements analysis and questions for the analyst**
- Every AC → a check; every check → a link to an AC or an explicit "extra heuristic" note.
- Surface ambiguities ("should work correctly", no concrete values, unspecified boundaries, undefined error behavior).
- Mismatches ticket ↔ Figma ↔ production ↔ docs — do NOT close with an assumption, write them up as questions.
- Record undefined behavior: empty states, network/server errors, timeouts, integration failure, concurrent actions, expired session.
- Clarify: validations (required fields, formats, masks, lengths, allowed characters, client vs server, error texts); permissions/roles (who sees/can, unauthenticated, missing permission); locale/formats (language, date/time/currency/numbers, TZ, text direction).
- All questions — as a list marked blocking/non-blocking; close blocking ones before starting.

**Prioritization and risk**
- Risk per area = defect probability × impact (money, security, data, reputation, usage frequency).
- Focus on changed code and its blast radius, not a uniform spread.
- Decide: what to automate (stable, regression-prone) vs manual checking (exploration, UX, one-off, visual).
- Carve out a smoke subset (critical for a quick build check) and a regress subset.
- Under a deadline, agree on depth explicitly, don't cut it silently.

**Plan / coverage matrix**
- Scope: what is in/out, on which environments/browsers/viewports.
- Matrix: browsers (Chromium/WebKit/Firefox) × viewports × roles × data states.
- Check classes: functional (happy/negative/boundary), UI/layout/responsive layout, validations, navigation/routing/deeplink, states (loading/empty/error/success), permissions/roles, integrations/API, data/persistence; non-functional (perf, security) where relevant.
- For each item: precondition → action → expected result → link to AC/source.
- Test data: valid/invalid/boundary, special characters, long strings, empty values, different roles/account states.
- Agree on exit criteria and report format BEFORE execution.

**Execution (evidence-based)**
- **Run scale.** Execute a large task (long multi-step flow, full screen regress, production/test comparison, release E2E) via fan-out (`references/fan-out.md`): the orchestrator drives the browser sequentially and collects artifacts, then parallel subagents (`Agent`) analyze them per axis, synthesis merges the findings. A small one (single page, smoke, one bug) — as a linear pass.
- Reproduce step by step; for each result — an observable artifact (screenshot, video, network response, console, DOM/DB dump).
- Distinguish: "works as expected" / "bug" / "question to requirements" / "not reproducible" — don't lump them together.
- Check not only the UI but also the network (status codes, payload, 4xx/5xx handling, retries, no sensitive data) and persistence (reload, re-login).
- Keep the console open for the whole run: JS errors/warnings, resource 404s, CSP/CORS.
- Verify post-action state in several layers: UI ↔ network ↔ DB/storage.
- Isolate the defect: minimal steps, frequency (always/intermittent), environment, build, preconditions; if flaky — repeat N times, record the frequency, don't mask it with a retry without understanding the cause.
- **Real input vs programmatic input.** Setting values programmatically (`fill()`, `setInputValue`, `.value=`, or an automation "type" that wraps them) may bypass the app's own event pipeline — framework `onChange`/`onBlur`, custom searchable/select components that commit only on option-click. The visible field shows text while the bound state stays empty → a false "required"/validation error (or, conversely, it masks a real one). Confirm any required/validation/selection finding with real user input (click the option, type character-by-character / `pressSequentially`, keyboard) before setting Pass/Fail. If the result depends on how the value was entered, it is not yet evidence.
- **Action map (page map) — don't re-learn the page.** The first pass over a screen is discovery; capture everything found (working selectors, order of custom controls, API endpoints, DOM quirks, the stand's console-noise baseline) into a run/project note right away. Run every subsequent check on that screen from the map with no re-discovery; wrap repeated flows (reaching step N of a wizard) into a helper script invoked as a single action. At the start of a new run, re-verify 1–2 key selectors from the map against the live page — they may have gone stale.
- **Browser tooling.** Interactive steps — via an MCP browser (Playwright / Chrome DevTools MCP). Repeated flows and page-map helper scripts — via `playwright-cli` (separate processes/profiles; scales to parallel agents, §7.8). Cross-browser: run critical scenarios (layout, scrolling, date pickers, focus/hover, file inputs) in at least two engines — Chromium + WebKit (a playwright-webkit MCP server or `playwright-cli --browser webkit`; iOS emulation when available): a sizable share of UI bugs is engine-specific and invisible in Chromium alone.
- **A workaround ≠ passing the step.** If the TC's target action cannot be performed the standard user way (click/tap/typing), that is a Fail (defect) or Blocked — even when a technical workaround exists (`focus()`, native setter, direct API call). A workaround is only allowed to unblock DOWNSTREAM checks, and it is stated explicitly in the report; the blocked step itself is never turned "green" via a workaround.

**Recording / DoD**
- Every test case with a status + evidence: Pass (artifact), Fail (bug + artifact), Blocked (reason), Not tested (why). Blocked ≠ Fail.
- Record results in the TMS strictly per the team's convention (comments, environment, attachments) — don't invent your own; evidence is kept in the run artifacts and the summary report regardless.
- Defects filed, linked to the ticket, severity/priority set, steps and artifacts attached.
- Coverage reconciled with AC: every AC covered by ≥1 check; uncovered ones — explicit with a reason.
- Run recorded: environment, build/commit, browsers/viewports, date, executor.
- Regression of affected areas done (or deliberately deferred with the risk recorded); blockers escalated; questions linked.
- New/updated test cases entered into the TMS; automation candidates flagged.
- **Negative gate (mandatory).** A run is NOT Done until negative and boundary classes are covered and cross-checked against `references/common-misses`; the report must include a "Negatives" section with a result per class or an explicit reason for skipping. "Simple/navigational object" is no excuse to skip negatives: a happy-path-only run is incomplete.
- **Done** = all non-blocked ACs checked with evidence, negatives/boundaries covered (or skip justified), bugs filed, report and test case statuses up to date, residual risks and uncovered items listed honestly.

---

## 1. Test design techniques

**Equivalence partitioning (EP)** — split input into classes (valid/invalid/special: empty, null, whitespace). One representative from each valid class; EVERY invalid class separately (different messages = different classes). Numbers: negative/0/positive/fractional/over the limit. Strings: Latin/Cyrillic/digits/special characters/emoji/RTL/case. Enumerations: each option + out-of-list. Files: allowed/forbidden/empty/corrupted. Dates: past/present/future/invalid format/nonexistent (Feb 31).

**Boundary value analysis (BVA) — exact boundaries ±1.** For [min..max] check exactly: min−1, min, min+1, max−1, max, max+1 (not "small/large"). String length: 0, 1, min±1, max±1. Boundary at 0: −1, 0, 1 (counters, balances, cart). Money: 0.00, min payment, min−0.01, max, max+0.01, cent rounding. Date/time: 23:59:59→00:00:00, last day of month, Feb 29 leap/non-leap, crossing midnight/year. Pagination: 0 items, exactly one page, page+1 items, last partial page. Age/term: exactly 18 (to the day), ±1 day, expiry exactly at the moment.

**Decision tables** — for business rules with condition combinations. Conditions × rules × expected action; cover every significant combination (not all 2^n); include impossible/contradictory ones (system rejects). Apply to: discounts/tariffs/calculations, feature access (role × flag × subscription × state), submit availability (field A × field B × checkbox), mutually exclusive conditions.

**State transitions (STT)** — for an entity with a lifecycle (draft→moderation→published→archived→deleted). Check every allowed transition and EVERY forbidden one (event in an invalid state → blocked). Transitions by timeout/system event (auto-cancel, session expiry); actions invalid in the current state (edit a published item, pay a canceled one); cycles/returns; state after interruption; concurrent transitions by two users.

**Pairwise / combinatorics** — when there are >3 parameters and full enumeration is unrealistic (OS × browser × role × language × theme). Generate a set covering all pairs (PICT/allpairspy); manually add critical business combinations pairwise may miss; check the defaults of each parameter.

**Error guessing** — for mature/legacy functionality via weak spots: double/triple click, submit before validation completes, special characters/injections, very long input (10k+), pasting large text, whitespace/zero-width, emoji, autofill, slow network, Back after success, F5 on an intermediate step, editing the payload in DevTools bypassing the UI, action with an expired token.

**Additionally:** cause-effect analysis (AND/OR/NOT between conditions, cascading/dependent fields); a CRUD matrix as the base skeleton for any entity; an access matrix (role × action × resource) + server-side enforcement check. **Always:** positive (valid classes, allowed transitions) + negative (invalid classes, forbidden transitions, UI bypass).

**Technique selection:** range/limit → BVA+EP; many parameters → pairwise; condition combinations → decision table; lifecycle → STT; dependent conditions → cause-effect; entity with data → CRUD; legacy → error guessing.

---

## 2. References (`references/`) — mandatory reading per task type

Detailed checklists live in `references/`. **Before drafting the plan, read (Read) each file relevant to the task in full** — not selectively and not from memory; a plan made without reading the reference counts as incomplete.

| File | When to read | What's inside |
|---|---|---|
| `references/frontend.md` | Any task with UI | Fields/forms (masks, limits, paste/autofill), visuals and all element states, Figma comparison, tokens, overflow, responsive layout and cross-browser (canonical resolutions) |
| `references/backend.md` | API / services / DB / integrations | HTTP methods and codes, schemas/contracts, pagination, idempotency, PATCH, DB (integrity, transactions, concurrency, migrations), AuthN/AuthZ/IDOR/multi-tenancy, queues/webhooks/cron, load and resilience, OWASP API Top 10 |
| `references/cross-cutting.md` | Almost always (frontend and backend together) | Network errors and mocks, UI↔Backend consistency, sessions/storage/multi-tab, navigation/deeplink, time/TZ/i18n, perf and console, security from the frontend, files/export, search/filters, payments, analytics |
| `references/artifacts.md` | Before recording results and bugs | Evidence, HAR/console, bug report structure, severity vs priority, deviations from the design, tracker/TMS, run summary report |
| `references/common-misses.md` | Always — before the final report | "Common misses" checklist: final self-check of run completeness |
| `references/fan-out.md` | Large run: long flow, full screen regress, production/test comparison | How to split a meticulous run across parallel subagents per axis: orchestrator collects artifacts → fan-out → synthesis. About the execution method, not a check class |

Minimal sets: UI task → frontend + cross-cutting (+artifacts when filing bugs); API/backend → backend + cross-cutting; full E2E/release → all. Large run / long flow → additionally `fan-out.md` at the execution stage. `common-misses.md` — always last, before producing the report.

---

> Apply the technique and track by task context. For each real task, check against its requirements and designs, not against this list as the truth — the list reminds you of check classes but does not replace AC and the source of truth.
