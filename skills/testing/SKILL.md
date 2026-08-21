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
- Find existing test cases (in your TMS — Zephyr/TestRail/other) and autotests (in the project's autotest repository): reuse, identify gaps, don't duplicate. Don't trust TMS statuses blindly — cross-check against the live tests: "Automated" with no existing autotest and "needs automation" on long-covered cases both happen.
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
- **RUN SIZE IS ESTIMATED BEFORE YOU START, AND THE EXECUTION METHOD IS AGREED WITH THE USER.** Before starting, count the volume: how many test cases, how many steps, how many viewports/browsers. If the size warrants fan-out (rule of thumb: >10 cases, full screen regress, long E2E) — **propose it to the user explicitly** and name the alternative with an estimate. A ban on launching subagents on your own does not ban PROPOSING them: the decision is the user's, and asking costs ten seconds. Silently defaulting to a linear pass and running out of context halfway is a planning failure — the run stalls unfinished and the user only learns about it after the fact. The same principle applies to any constraint that can derail the task midway (no test data, the environment is down, an integration is unavailable, access is missing) — raise it at the start, not when you hit the wall.
  - **A linear pass is also a decision, and its cost is estimated up front.** One case ≈ reading the card + 2-4 browser calls + screenshots; reading a screenshot as an image costs more than everything else. If the estimate does not fit — do not start hoping you will make it; cut the methodology deliberately and say so.
  - **When fanning out, assign agents to DIFFERENT browser servers** (playwright / webkit / ios / chrome-devtools, etc.) and state this in each agent's prompt: parallel agents on one browser fight over the tab and corrupt each other's run. Hand each agent a page map (working selectors, quirks, known defects) — otherwise every one of them burns time on rediscovery.
  - **Clean up after yourself, and verify the cleanup in the process list.** When the run ends, close the browsers (every MCP you opened), remove mocks (`unrouteAll`), stop any servers you started, delete temporary files. Abandoned sessions linger in the background and interfere with the next run.
    - **In headless mode a forgotten browser is invisible — neither you nor the user will notice it.** So cleanup ends not with the close call but with a check of the process list by automation markers (`--allow-pre-commit-input`, `--disable-field-trial-config`, `--inspector-pipe`): empty output = clean. The user's own browser carries none of these flags and never matches the filter.
    - **Not every browser MCP exposes a "close browser" call** (some only close a tab, and the last tab cannot be closed) — there cleanup means terminating the browser process by its automation marker or temp-profile path, WITHOUT killing the MCP server itself.
    - Cleanup is mandatory after intermediate runs inside a task (testing a hypothesis, reproducing a bug), not only at the very end: contexts created programmatically stay alive in the browser until closed.
- Reproduce step by step; for each result — an observable artifact (screenshot, video, network response, console, DOM/DB dump).
- Distinguish: "works as expected" / "bug" / "question to requirements" / "not reproducible" — don't lump them together.
- **YOUR MEASURING INSTRUMENT LIES MORE OFTEN THAN THE PRODUCT. A selector, regex or script is itself under test, not a source of truth.** Real misses: the regex `/Check the/` matched the subheading "Check the number" instead of the error; a modal lookup by phrase matched the same wording in a banner and reported "modal open" where there was none; `innerText` with line breaks failed to match the reference on a perfectly correct screen; a filter dropped part of the messages and one error was counted instead of six.
  - **Any unexpected result — inspect the instrument first, the product second.** "Nothing found", "found the wrong thing", "found one instead of six", "element not found" are, first of all, hypotheses about your selector.
  - **Confirm with your eyes what the script counted.** The screenshot and its visible text are the arbiter; a DOM query proves what you already saw.
  - **Substring matching is unreliable.** Use whole unique phrases, scope the search to a container (look for the error inside the field's block, not across the page), assert the COUNT of matches rather than mere presence. Normalise text with line breaks before comparing.
- **BLOCKED MEANS THE CASE CANNOT BE EXECUTED, NOT THAT YOU KNOW IT WILL FAIL.** If the steps are executable and the object is reachable — run it and record Fail with evidence, even when the defect is already filed and the outcome is predictable. Blocked is only for missing access, data or environment. A wrong Blocked hides the case from the run and creates false "not covered": two status-check cases sat unexecuted this way while each failed within a minute and produced ready-made evidence for the adjacent team.
- **BEFORE DECLARING "THIS CANNOT BE CHECKED" — INVENTORY WHAT ALREADY EXISTS.** Look through the task's working folder, previously collected artefacts, scripts and mocks, your own earlier notes and project memory: the needed tool has often already been built within this very task. Real case: a test case was declared unverifiable "needs a mock server" while the mock server sat in the project folder, written a week earlier for the same task. "Impossible" is only allowed after checking what is available.
- Check not only the UI but also the network (status codes, payload, 4xx/5xx handling, retries, no sensitive data) and persistence (reload, re-login).
- Keep the console open for the whole run: JS errors/warnings, resource 404s, CSP/CORS.
- Verify post-action state in several layers: UI ↔ network ↔ DB/storage.
- Isolate the defect: minimal steps, frequency (always/intermittent), environment, build, preconditions; if flaky — repeat N times, record the frequency, don't mask it with a retry without understanding the cause.
- **INPUT IS ALWAYS REAL — this is the default, not a special case.** Every value goes into every field the way a user enters it: click the field → type character-by-character on the keyboard (`pressSequentially`, `keyboard.press`, `insertText`) → leave focus by click or Tab. Dropdowns: click the option. Checkboxes/radios: click the visible control. Files: through the real dialog. Setting values programmatically (`fill()`, `setInputValue`, `.value=`, native setter + `dispatchEvent`, or an automation "type" that wraps them) bypasses the app's own event pipeline — framework `onChange`/`onBlur`, masks, debounces, custom components that commit only on option-click.
  - **Both directions of error are equally dangerous.** Programmatic input produces false Fails (the field shows text while state is empty → "required" on a filled form) *and* false Passes — **validation simply never runs, so an invalid value looks accepted**. The second is worse: it files a defect that does not exist while the real one stays unfound.
  - **Programmatic input is acceptable ONLY to set up preconditions** — quickly filling the uninteresting fields to reach the step under test. The field you are testing right now is always entered for real, no exceptions.
  - **Leaving focus is a real action too.** `dispatchEvent(new Event('blur'))` and `el.blur()` are NOT equivalent to a real Tab or a click elsewhere: React listens for `focusout` through its own event system, and a synthetic `blur` never reaches the handler. A field is blurred **only** by a real `Tab` or a click on another element. This is its own trap: fields with live validation (email, phone, date) will still show the error on a programmatic blur, while fields validated on blur (names, latin-only) will not. The result is a mixed picture where some checks "work", making it easy to conclude the method is sound.
  - **A Pass/Fail verdict on validation, masks, required, boundaries or formats obtained via programmatic input or programmatic blur is void.** Not "confirm if in doubt" — do not issue the verdict at all until you have repeated it by hand. If the result depends on how the value was entered, that is a finding about the input method, not about the product.
  - **"No error" is the most suspicious result there is.** Before writing "validation is missing", always repeat with click + character-by-character typing + Tab. A missing error almost always means the event never reached the validator, not that the validator does not exist.
  - **"THE ELEMENT IS MISSING" IS A CLAIM ABOUT ALL STATES, NOT THE ONE STATE YOU LOOKED AT.** Before writing "the clear icon / button / hint / icon is not displayed", walk the states in which the element may appear: focus and blur, hover, empty and filled value, before and AFTER the first successful action (check, submit, load), after an error, different viewports. The display condition is often a disjunction ("after the check OR on blur"): if you checked one branch and found nothing, you found nothing in one branch — not "missing entirely". Real case: a clear icon was reported as a defect because it is absent while the field is focused; in fact it appears after the first successful certificate check or after blur — neither branch was checked.
    - **Red flag: the user or developer says "but it's right there" while you see nothing.** That almost always means you looked in a different state, not that they imagined it. Do not argue or double down on your measurement — find out under which conditions they see it and reproduce THEIR exact scenario.
    - When describing element behavior in a report or test case, give a state matrix, not a single line: "focused: absent / after blur: present / after check: present" — otherwise the next run files the same false defect again.
  - **A SUBAGENT'S FINDING IS A HYPOTHESIS UNTIL YOU HAVE VERIFIED IT YOURSELF.** You see the agent's conclusion but not the path to it: a wrong selector, a fragment of the picture presented as the whole, a sloppy mockup comparison all look exactly as convincing as a real defect. Before filing a defect or handing a finding to a developer — reproduce it personally with your own measurement. Especially when the finding reads as "something is missing from the screen" or "diverges from the mockup" (open the mockup and look yourself). Passed checks do not need re-asking — you re-verify what goes out the door.
- **A MOCK TESTS BEHAVIOUR, NOT CONTENT. Whatever you put into the stub yourself cannot be a finding — it is an echo of your mock, not a defect in the product.** Writing `{"message":"Internal Server Error"}` into `route.fulfill`, then seeing "Internal Server Error" on screen and filing "the user is shown a technical message" is circular reasoning: you planted the data and then "discovered" it. That files a defect that does not exist and burns the team's time.
  - **On a stub you only verify the app's reaction:** the UI does not hang, fields and buttons unlock, entered data survives, no success screen appears by mistake, how many requests went out, whether retry fired, whether a notification appeared **at all**.
  - **On a stub you do NOT verify:** the message wording or language, the error code, the response format and structure, the icon or colour — you set all of that yourself.
  - **Texts, codes and formats are verified only against a real response from the system** — a live request, a reproduction of an actual failure, or a mock server that mirrors the contract (texts taken from the swagger/docs/live response, not invented). A stub with a made-up body cannot support any conclusion about content.
  - **Before filing a defect about anything on screen, ask: where did this value come from?** If it came from your stub, your test data or your override, there is no defect. There is a defect only when the system produced the value.
- **"THE MOCK IS REMOVED" IS VERIFIED, NEVER ASSUMED. A forgotten route turns every later check into fiction.** `page.unroute(pattern)` removes an interception ONLY on a character-for-character match of the pattern string: a route registered as `'**/api/wb/submit-policy'` is NOT removed by `unroute('**/api/wb/**')` — Playwright compares strings, not URL coverage. The mock stays alive for the whole session and every subsequent run receives a fabricated response that gets mistaken for product behaviour.
  - **Use `page.unrouteAll()`** or the exact same pattern you registered. Register and remove in the same place, side by side.
  - **After removing, issue a control request** before drawing any conclusion: perform the action under test and confirm the response is real (status, body, side effect such as a created record).
  - **RED FLAG: your tool and the browser disagree on an identical request.** curl/API client returns 200 while the browser returns 5xx, with byte-identical payload and headers → 99% of the time this is your own interception, not a defect. **Remove all mocks and repeat first**, and only then look for a cause in the product, proxy, CORS or network.
  - **Do not build a multi-step defect investigation before proving the environment is clean.** Comparing headers, theorising about Origin and infrastructure — all of it is wasted if your own stub sits on top. First prove you are looking at the real system.
  - **Between scenarios the environment returns to its initial state:** routes removed, `setOffline(false)`, throttling/permissions/storage restored. Any unclosed override leaks into the next checks and corrupts them silently.
- **Action map (page map) — don't re-learn the page.** The first pass over a screen is discovery; capture everything found (working selectors, order of custom controls, API endpoints, DOM quirks, the stand's console-noise baseline) into a run/project note right away. Run every subsequent check on that screen from the map with no re-discovery; wrap repeated flows (reaching step N of a wizard) into a helper script invoked as a single action. At the start of a new run, re-verify 1–2 key selectors from the map against the live page — they may have gone stale.
- **Browser tooling.** Interactive steps — via an MCP browser (Playwright / Chrome DevTools MCP). Repeated flows and page-map helper scripts — via `playwright-cli` (separate processes/profiles; scales to parallel agents, §7.8). Cross-browser: run critical scenarios (layout, scrolling, date pickers, focus/hover, file inputs) in at least two engines — Chromium + WebKit (a playwright-webkit MCP server or `playwright-cli --browser webkit`; iOS emulation when available): a sizable share of UI bugs is engine-specific and invisible in Chromium alone.
- **A workaround ≠ passing the step.** If the TC's target action cannot be performed the standard user way (click/tap/typing), that is a Fail (defect) or Blocked — even when a technical workaround exists (`focus()`, native setter, direct API call). A workaround is only allowed to unblock DOWNSTREAM checks, and it is stated explicitly in the report; the blocked step itself is never turned "green" via a workaround.
- **A RETEST AFTER FIXES IS A CHECK AGAINST TWO BASELINES: the mockup AND the previous run.** Fixing one property moves the neighbors: real case — fixing the carousel container height silently broke the centering between the arrow buttons and the bottom spacing; both regressions were caught by the client, not by the run.
  — **Diff coordinates against the previous run.** A changed number (x/y/w/h) that the fix does not explain is a regression signal, not noise: "x was 419, became 360" must be followed up even if the element itself looks fine.
  — **Measure MUTUAL positioning, not just the element itself:** gaps to the left/right neighbors, equality of paired margins, center alignment (element ↔ container ↔ viewport). "The card is the right size and in place" does not catch that the arrows now sit at different distances.
  — **Open with your eyes the screenshot of EVERY width and state you checked.** A screenshot taken but never opened = a state never verified; "the numbers match" does not replace looking.
  — **An element screenshot of a container clips protruding children** (fixed height, transforms, negative margins) — content looks "cut off" on such a shot, but that is a capture artifact. For visual comparison shoot the whole block or the viewport; element shots are only for close-up zoom.
  — **After a fix re-verify the whole affected node and the adjacent test cases**, not only the step that used to fail.

**Recording / DoD**
- Every test case with a status + evidence: Pass (artifact), Fail (bug + artifact), Blocked (reason), Not tested (why). Blocked ≠ Fail.
- Record results in the TMS strictly per the team's convention (comments, environment, attachments) — don't invent your own; evidence is kept in the run artifacts and the summary report regardless.
- Defects filed, linked to the ticket, severity/priority set, steps and artifacts attached.
- Coverage reconciled with AC: every AC covered by ≥1 check; uncovered ones — explicit with a reason.
- Run recorded: environment, build/commit, browsers/viewports, date, executor.
- Regression of affected areas done (or deliberately deferred with the risk recorded); blockers escalated; questions linked.
- New/updated test cases entered into the TMS; automation candidates flagged.
- **Don't lose findings when summarizing.** Any anomaly noticed during the run (even one that seemed minor or "self-healing" at the time) must reach the summary — as a bug or a question. Judging it "not critical" is no license to omit it: a finding dropped from the report = a missed defect. Especially a false/stuck validation error (see `references/common-misses`).
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
