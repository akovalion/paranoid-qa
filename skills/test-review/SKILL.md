---
name: test-review
description: Review of just-written or modified autotests against TypeScript + Playwright best practices (per official documentation) and your project's conventions. Use via /test-review or after writing/editing any test (UI E2E, API, UI+API, mocks, visual, mobile) or a Page Object/fixture/constants — before commit. Produces a prioritized list of findings with severity, line references, and ready-made fixes.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - AskUserQuestion
---

# Autotest review (TypeScript + Playwright)

Check just-written or modified test code against best practices and produce a prioritized list of findings with fixes. Rule source — the **official Playwright documentation** ([best-practices](https://playwright.dev/docs/best-practices), [locators](https://playwright.dev/docs/locators), [test-assertions](https://playwright.dev/docs/test-assertions)) and [TypeScript](https://playwright.dev/docs/test-typescript) + the specific project's conventions.

> **Source of truth for the project** — its root `CLAUDE.md` (if present) and the style of neighboring code. This skill is the **review phase**: it complements project rules, it does not replace them. Expanded `❌ before → ✅ after` examples and source links for each rule — in [`references/rules-catalog.md`](references/rules-catalog.md).

---

## When to apply and operating mode

- **Default mode — diagnostics.** Read the code, run static analysis, produce a report. Do **not** edit files until the user explicitly asks to "apply / fix". Then — **iteratively**, one change at a time with a run in between (no big-bang rewrite of a working test).
- **Scope — only new/changed code, not the whole suite.** Default — uncommitted changes (`git status` + `git diff`). If the user specified a file/directory — review those.
- **Any test type:** UI E2E, API, UI+API, visual regression, mobile, mocks, plus Page Objects, fixtures, constants.
- Do not drift into autonomous actions beyond the review (browser reproduction, running the whole suite, edits) without confirmation — the default task is "read and assess".

## Evidence discipline (no hallucinations)

- Every finding — from an **actually read line** (`file:line`) or from **observed output** of typecheck / lint / a run. Do not invent violations "by analogy" and do not reference lines you have not seen.
- A rule is checkable by a tool (tsc, ESLint, a run) → **run the tool first, then report its output**, not "probably present".
- Not sure it is a defect rather than a deliberate project decision → mark it **"questionable"**, do not assert. Cross-check against the project's `CLAUDE.md` and neighboring code: some "anti-patterns" may be intentional (legacy helpers, non-standard markup, deliberate rule exceptions). File names/endpoints/selectors from memory and past context are background — re-verify against live code.
- Found no violations in a category — say so: "clean", do not invent a finding for volume.

## Process

1. **Scope.** Determine the files under review: `git status --short` + `git diff --name-only` (include untracked), or the paths provided. For each spec, find the related Page Objects, constants, fixtures.
2. **Context.** `Read` the changed files + related POM/constants/fixtures. `Read` a neighboring spec in the same directory as a style reference. Cross-check the directory/suite rules (smoke / regress / api etc.) against the project's `CLAUDE.md`, if present.
3. **Static analysis (mandatory — cheap and evidence-based):**
   - Typecheck: `tsc --noEmit` (or the project's typecheck script from `package.json`). Any type error in new code = 🔴 Blocker.
   - ESLint: find the project config and **read which rules are actually enabled** (especially from `eslint-plugin-playwright`) — do not assume from memory. Lint output is the source of truth.
   - **What lint actually catches — a two-level check.** (1) No eslint-plugin-playwright at all → floating promises, manual asserts and `networkidle` are invisible; suggest enabling recommended. (2) Recommended is on → `missing-playwright-await`, `prefer-web-first-assertions`, `no-networkidle` are already errors and get caught, but `no-wait-for-timeout`, `no-force-option` and `expect-expect` are only **warn** there (verified against v2.10.5) — without `--max-warnings 0` these warnings never fail CI. Suggest raising them to error. `@typescript-eslint/no-floating-promises` needs type-aware linting — rarely enabled. Whatever lint still misses — verify manually (A/C/H).
   - If needed — a formatting check (Prettier), if configured in the project.
4. **Checklist.** Go through categories A–J below + K (your project's rules). For each violation — severity + `file:line` + fix. Deeper per rule — [`references/rules-catalog.md`](references/rules-catalog.md).
5. **Stability verification** (only if the user asks to confirm the test works and a sandbox is available): run **only this test** in the project's native parallelism (NOT `--workers=1`):
   ```bash
   npx playwright test <file> --grep "<id>" --project="<projectName>" --retries=0 --repeat-each=5
   ```
   Pass-on-retry or a floating result = flake = 🟠 Major; fix the cause (races/hydration/waits), do not hide it behind retries.
6. **Report** — in the format from the "Report format" section.

## Severity

| Label | Meaning | Typical examples |
|---|---|---|
| 🔴 **Blocker** | Test is broken, non-deterministic, or masks a bug. Do not merge. | Typecheck error; missing `await` (floating promise); `waitForTimeout`/in-page `setTimeout` pause; pass only on retry; `{ force: true }` / `dispatchEvent` / direct `setter` bypassing the real UI; test without asserts; `test.only`; conditional `expect` that may never execute. |
| 🟠 **Major** | Brittleness or flake on content/environment change; violation of a key project rule. | CSS/XPath chains instead of role/label; instant `count()`/`isVisible()`/`allTextContents()` as a gate; exact prices/texts/dates instead of regex; project convention violation (importing base `@playwright/test` where the project requires a custom fixture; a mandatory project check skipped — e.g. the network error monitor); `waitForLoadState('networkidle')`; a test depends on another test's state. |
| 🟡 **Minor** | Style/readability/maintainability; no impact on stability. | No `test.step` for business steps; inline comments instead of self-documentation; `.nth()` where `.filter()` fits; a working but non-priority locator; unused import/constant. |
| ⚪ **Nit** | Cosmetics. | Naming, import order, formatting (if not caught by Prettier). |

---

## Review checklist

Each item — what to look for; the violation's severity in parentheses. Expanded examples and proofs — in the catalog.

### A. Determinism, waits, asynchrony
- [ ] No `page.waitForTimeout(ms)` and no `setTimeout`/`sleep` inside `page.evaluate` (grep for both). Wait for state, not time. (🔴)
- [ ] No floating promises: every `expect`, `test.step`, action (`click/fill/goto`), `waitFor*` — under `await`/`return`/`void`. A missing `await` = silent flake. (🔴)
- [ ] Network — the **promise → action → await** pattern: `const p = page.waitForResponse(...); await click(); await p`. Declaring after the action = race. (🔴)
- [ ] No `waitForLoadState('networkidle')`. Navigation — `goto(url, { waitUntil: 'domcontentloaded' })`, without a duplicate `waitForLoadState` right after. (🟠)
- [ ] Derived/compound checks (several related conditions, measuring a collection right after it appears) — in `await expect(async () => {...}).toPass({ timeout })`, not a chain of `await`s. (🟠)
- [ ] SSR hydration accounted for: SSR frameworks (Nuxt/Next etc.) can remount content after hydration → an instant `count()`/`allTextContents()` right after appearance hits the emptiness window. Measure via `toPass`. (🟠)

### B. Locators
- [ ] Priority: `getByRole({ name })` → `getByText` → `getByLabel` → `getByPlaceholder` → `getByAltText` → `getByTitle` → `getByTestId` → CSS (last resort) → XPath (almost never). (🟠 for CSS/XPath without a reason)
- [ ] No brittle CSS chains tied to DOM structure (`div > div > span`, `.episode-actions-later`). They break on rebranding. (🟠)
- [ ] Strict mode: the locator resolves to a single element; narrow via `{ name }` / `.filter({ hasText })` / `.filter({ has })`, not `.nth()`. `.nth()` — only with justification. (🟡)
- [ ] Floating elements (dropdowns, toasts, modals, portal content, iframes) are located **globally from `page`**, not from a section. (🟠)
- [ ] A long `getByText('whole sentence')` is not used as an anchor — brittle to copy edits; take a stable fragment/role. (🟡)

### C. Assertions
- [ ] Only **web-first** (auto-retrying): `toBeVisible/toHaveText/toHaveCount/toHaveValue/toBeChecked/toHaveAttribute/toHaveURL`. No `expect(await loc.isVisible()).toBe(true)` and `expect(await loc.count()).toBe(n)` — they do not retry. (🔴/🟠)
- [ ] Every test verifies something (no test that only clicks without an `expect`). (🔴)
- [ ] A block of independent checks for one section — via `expect.soft`, to collect all failures at once. (🟡)
- [ ] No asserts on exact prices/numbers/dates/dynamic content — regex or a range. (🟠)
- [ ] A known open bug — `test.fail()` (with the single bug assert), not `test.fixme()`; the working behavior — as a separate regular test. (🟡)

### D. Isolation and independence
- [ ] Tests are independent: state is NOT passed between tests. `let x` at `describe` level, reinitialized in `beforeEach`, is a common valid pattern; the violation is a test reading another test's result. Must pass in isolation and in any order. (🔴 if isolation is broken)
- [ ] `describe.configure({ mode: 'serial' })` — only for a real dependency, not "just in case". (🟠)
- [ ] Setup/teardown — in `beforeEach`/fixtures, no copy-paste; created entities (API) are deleted. (🟠)
- [ ] The test does not depend on external sites and third-party widgets — test only what you control; for the external part — mock/verify the request was made. (🟠)

### E. TypeScript and lint
- [ ] Typecheck green for new code (`tsc --noEmit`, strict). (🔴)
- [ ] `any` in **POM / fixtures / utils** — undesirable, type it (`Locator`/`Page`/`Route`/`APIResponse`). Cross-check the project config: `any` may be deliberately allowed in specs (e.g. for mock data) — do not flag it there. `@ts-ignore` — only with a reason/ticket. (🟠 for POM/utils)
- [ ] POM fields — `readonly Locator`; fixtures typed (`base.extend<{...}>`); type the API response body explicitly if asserts rely on it. (🟡)
- [ ] **A missing `await` is often NOT caught by lint** (check the config: is `no-floating-promises` / `missing-playwright-await` there; `valid-expect` covers only part) → re-read by eye, see A2. (🔴)
- [ ] Match the module system (ESM vs CJS) and import style (relative vs aliases) against the project's actual code — follow the existing style, do not impose your own. Remove unused imports/variables/constants/POM methods. (🟡)

### F. Network and mocks
- [ ] Mocks (`page.route`) — only for edge cases (5xx, empty response, timeout, offline). The positive happy path — against the real API. (🟠)
- [ ] Contract verification where it is the point of the test: `waitForResponse` (status + body) / `waitForRequest` + `postDataJSON()`. For forms — inspect the payload for `[object Object]`, empty/non-serialized fields, not just "button is enabled". (🟠)
- [ ] Routes are set up **before** the triggering action; scope — test/fixture, not globally on the suite. (🟠)
- [ ] An external host that may not respond (e.g. an external account portal, a payment gateway): do not verify the transition "in depth" — the oracle is the initiated navigation request + `route.abort()`, otherwise a pending navigation hangs teardown. (🟠)

### G. Structure, readability, hygiene
- [ ] Logical steps are wrapped in `test.step('Imperative name', …)` (visible in Allure/HTML/trace). `return` — outside the callback. Do not split into a step per action. (🟡)
- [ ] **No inline comments** in tests — self-documentation (meaningful names, semantic locators, steps). Context — in the reporter description/annotation (e.g. `allure.description`), if the project uses them. (🟡)
- [ ] Parameterize same-shaped cases via `for...of` **outside** `test.describe`, not test copies. (🟡)
- [ ] No `test.only`, commented-out tests, temporary files/drafts, debug `console.log`/`page.pause()`. (🔴 for `test.only`/`page.pause`, otherwise 🟡)
- [ ] Test/step names are meaningful; ID/tag format (`@allure.id:N`, TC key etc.) — as in the neighboring tests in the file. (⚪)

### H. Bug masking and flake
- [ ] No synthetic bypasses of the real UX: `{ force: true }`, `dispatchEvent`, direct React/Vue setter, manual scroll instead of auto-actionability — unless justified by a controlled input (e.g. custom `display:none` inputs — verify in the browser). The fix must catch a regression if the feature breaks, not hide it. (🔴)
- [ ] `retries`/`mode: serial`/an increased timeout are not used as a "cure" for flake. Quarantine is acceptable only temporarily, with a ticket link. (🟠)
- [ ] `try/catch` does not swallow action/assert failures (auto-waiting is built in; `.catch()` hides the bug). (🟠)
- [ ] A pre-release test (written before the feature ships) **fails honestly**, not hidden behind `skip`/a flag. (🟠)

### I. Special cases by test type
- [ ] **API:** verify status AND body; request identifiers — a fresh `randomUUID()` from the built-in `crypto` per request (do not pull in the `uuid` package if the project does not have it); rate limit accounted for; cleanup of created entities. (🟠)
- [ ] **iframe:** `frameLocator`; content is located inside the frame. **New tab:** `context.waitForEvent('page')`. **Download:** `waitForEvent('download')` + filename check. **Upload:** `setInputFiles`. **Time:** `page.clock`. **Geolocation/permissions:** `grantPermissions`/`setGeolocation`. (🟠 for manual workarounds)
- [ ] **visual:** `toHaveScreenshot` with `animations:'disabled'` and `mask` on dynamic content; baselines — on the CI platform (a macOS baseline against Linux CI = guaranteed diff). Only if the test case requires a baseline. (🟠)

### J. Intent conformance (the oracle actually verifies what is claimed)
- [ ] The test verifies what the name/description promises, not a surrogate. "Form validation" → inspect the real payload, not just "button is enabled". "Load more" → actual loading of more items and verification, not just the click. (🟠)
- [ ] Content binding is structural (presence, non-emptiness, `count > 0`, regex), so the test survives copy/price changes — especially for regression tests after a fix. (🟠)
- [ ] The oracle matches the environment's limitation: where the UI does not distinguish 404/5xx (one stub for both) — the check is network-level, not "saw the error text". (🟠)

### K. Your project's rules (template — fill in for your repository)
> A mature test repository always has conventions no universal checklist will catch. Record them here or in the project's `CLAUDE.md` — then the review will catch their violations. Typical categories with examples:

- [ ] **Custom fixtures:** where to import `test` from the custom fixture (`./fixtures/custom-test`) instead of `@playwright/test`, and which mandatory checks it provides (e.g. a network error monitor invoked at the end of the test / in `afterEach`). (🟠)
- [ ] **Directory patterns:** how the rules of the smoke / regress / api suites differ — composition vs fixtures for POM, reporter annotations, testMatch/testIgnore, where to add new tests. (🟠)
- [ ] **Environments:** the test and POM are verified on all target environments, not just one (the DOM on the test environment may differ from prod); known environment quirks are recorded as a list. (🟠)
- [ ] **Skipped hygiene:** the test does not add permanent skips to standard runs; environment-specific exclusion goes through config (`testIgnore`/`testMatch`), runtime `test.skip` — only for dynamic conditions (feature flag, known bug with a ticket). Run outcome: passed = ok, failed = problem, skipped = requires an explanation. (🟡)
- [ ] **Dependencies/config:** do not bump the `@playwright/test` version and do not add dependencies without checking against CI (Docker image, lock file); do not touch `playwright.config.ts` without necessity. (🔴 if touched without being asked)

---

## Report format

```
## Review: <files / scope>

**Static analysis:** typecheck ✅/❌ · lint ✅/❌ · (run: N/N pass, --repeat-each=5)

### 🔴 Blocker (N)
1. `path/to/spec.ts:42` — <what is wrong>.
   Why: <link to rule/category>.
   Fix:
   ```ts
   // ❌ before / ✅ after
   ```

### 🟠 Major (N)
…

### 🟡 Minor (N)
…

### ⚪ Nit (N)
…

### ✅ What is good
- <what matches best practice — brief>

### Verdict
<Ready to commit / Needs rework: list of Blocker+Major> · <run command with the correct --project>
```

Rules:
- Sort strictly by severity (Blocker → Nit). Within a level — by file/line.
- Every Blocker/Major — with a concrete fix (a `❌ before → ✅ after` snippet).
- A category is clean — write "clean", do not invent.
- At the end — a one-line verdict and the run command with the correct `--project`.
- If asked to apply fixes — do it **iteratively** (one change → typecheck/run → the next), do not rewrite a working test wholesale.
