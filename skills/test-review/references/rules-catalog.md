# Review rules catalog — `❌ before → ✅ after`

Companion reference to the `SKILL.md` checklist. Every rule: severity, what the violation looks like, how to fix it, why. Categories A–K match the checklist.

**Sources:** rules marked **PW** are backed by official Playwright documentation (`playwright.dev/docs/...`) — link at the rule. The rest are engineering practice, with rationale in the rule text. Category K covers your project's conventions (source — its `CLAUDE.md` and code).

---

## A. Determinism, waits, asynchrony

### A1. `waitForTimeout` and in-page pauses — 🔴
A blind pause is slow and flaky at the same time (on CI the element may appear later).
```ts
// ❌
await page.click('button');
await page.waitForTimeout(2000);
expect(await page.locator('.result').count()).toBe(3);

// ✅
await page.getByRole('button', { name: 'Show' }).click();
await expect(page.getByRole('listitem')).toHaveCount(3);
```
Grep not only for `page.waitForTimeout` but also for `setTimeout`/`sleep` inside `page.evaluate(...)` — it hides there too.
Source: PW [best-practices#use-web-first-assertions](https://playwright.dev/docs/best-practices).

### A2. Missing `await` (floating promise) — 🔴
The promise is not awaited → the test moves on before the action/assertion completes → non-deterministic "sometimes passes".
```ts
// ❌
expect(page.getByText('Done')).toBeVisible();   // won't wait
test.step('Submit', async () => { ... });       // step won't run synchronously

// ✅
await expect(page.getByText('Done')).toBeVisible();
await test.step('Submit', async () => { ... });
```
**Important:** many configs have NEITHER of the needed rules (neither `@typescript-eslint/no-floating-promises` nor `eslint-plugin-playwright/missing-playwright-await`) → lint will miss floating promises; `valid-expect` only catches some `expect` forms. Check the project config; if the rules are absent — **re-read by eye** and suggest adding both.
Source: PW [best-practices#lint-your-tests](https://playwright.dev/docs/best-practices).

### A3. Race when waiting for network — 🔴
Declaring `waitForResponse`/`waitForRequest` **after** the action loses the event.
```ts
// ❌
await page.getByRole('button', { name: 'Submit' }).click();
const res = await page.waitForResponse('**/api/submit');  // the click may have already fired

// ✅
const resPromise = page.waitForResponse(r => r.url().includes('/api/submit') && r.request().method() === 'POST');
await page.getByRole('button', { name: 'Submit' }).click();
const res = await resPromise;
```
Source: PW [events#waiting-for-event](https://playwright.dev/docs/events).

### A4. `networkidle` and redundant `waitForLoadState` — 🟠
`networkidle` is unreliable on heavy SPAs (constant background requests) and is marked discouraged in the docs.
```ts
// ❌
await page.goto('/checkout');
await page.waitForLoadState('networkidle');

// ✅
await page.goto('/checkout', { waitUntil: 'domcontentloaded' });
// then a web-first wait for the target element, no duplicate waitForLoadState
```
Check whether `no-networkidle` is enabled in the project config — if not, lint won't catch it, check by eye.
Source: PW [navigations](https://playwright.dev/docs/navigations).

### A5. Instant read as a gate instead of `toPass` — 🟠
`count()`/`allTextContents()`/`isVisible()` don't retry → they capture an intermediate state (re-render, hydration).
```ts
// ❌
const items = await page.getByRole('listitem').allTextContents();
expect(items.length).toBeGreaterThan(5);

// ✅ — wrap a compound/derived check in toPass
await expect(async () => {
  const items = await page.getByRole('listitem').allTextContents();
  expect(items.length).toBeGreaterThan(5);
  expect(items.every(t => t.trim())).toBe(true);
}).toPass({ timeout: 10_000 });
// or a single condition — as a regular web-first assertion:
await expect(page.getByRole('listitem')).toHaveCount(12);
```
Collecting data via `count()`/`allTextContents()` is fine — but **after** a web-first wait for stability, not right after the element appears.
Source: PW [test-assertions#expecttopass](https://playwright.dev/docs/test-assertions).

### A6. SSR/hydration (Nuxt/Next/similar) — 🟠
An SSR app may remount content during hydration → a collection visible in the initial HTML briefly goes empty and re-renders.
```ts
// ❌ — a read right after the container appears hits the empty window
await form.waitFor();
const fields = await form.getByRole('textbox').count();   // may be 0

// ✅
await expect(async () => {
  expect(await form.getByRole('textbox').count()).toBe(4);
}).toPass();
```
A common trap on landing pages and forms of SSR frameworks; see also A5.

---

## B. Locators

### B1. Locator priority — 🟠 for CSS/XPath without justification
Official order: `getByRole({ name })` → `getByText` → `getByLabel` → `getByPlaceholder` → `getByAltText` → `getByTitle` → `getByTestId` → CSS (last resort) → XPath (almost never).
```ts
// ❌
page.locator('button.buttonIcon.episode-actions-later');
page.locator('div.card > div.body > span.title');

// ✅
page.getByRole('button', { name: 'Submit' });
page.getByRole('listitem').filter({ hasText: 'Shipping' }).getByRole('heading');
```
CSS/XPath are tied to DOM structure and break on redesign; role locators reflect how users and AT perceive the page.
Source: PW [locators](https://playwright.dev/docs/locators), PW [best-practices#use-locators](https://playwright.dev/docs/best-practices).

### B2. Strict mode and `.nth()` — 🟡
A locator must resolve to a single element; positional selection is brittle (page changed → different element).
```ts
// ❌
page.getByRole('listitem').nth(2);

// ✅
page.getByRole('listitem').filter({ hasText: 'Premium' });
page.getByRole('row', { name: 'Smith' }).getByRole('button', { name: 'Delete' });
```
`.nth()`/`.first()`/`.last()` — only when the element genuinely cannot be selected by meaning, with a justifying comment.
Source: PW [locators#strictness](https://playwright.dev/docs/locators).

### B3. Floating elements — globally from `page` — 🟠
Dropdowns, toasts, modals, portal content, and iframes often render outside their source section (at the end of `body`).
```ts
// ❌ — the dropdown won't be found inside the section
section.getByRole('option', { name: 'London' });

// ✅
page.getByRole('option', { name: 'London' });
```

### B4. Long text as an anchor — 🟡
`getByText('an entire subheading sentence')` breaks on any copy edit.
```ts
// ❌
page.getByText('Set up your subscription online in 5 minutes, no office visit');
// ✅
page.getByRole('heading', { name: /subscription/i });
```

---

## C. Assertions

### C1. Web-first instead of manual — 🔴/🟠
`isVisible()`/`count()` return instantly and don't retry.
```ts
// ❌
expect(await page.getByText('Welcome').isVisible()).toBe(true);  // 🔴 (flaky)
expect(await loc.count()).toBe(3);                               // 🟠

// ✅
await expect(page.getByText('Welcome')).toBeVisible();
await expect(loc).toHaveCount(3);
```
Web-first (auto-retry until timeout): `toBeVisible/toHaveText/toContainText/toHaveCount/toHaveValue/toBeChecked/toBeEnabled/toBeDisabled/toHaveAttribute/toHaveClass/toHaveURL`. Check the config: if `prefer-web-first-assertions` is not enabled — lint won't catch manual assertions, check by eye.
Source: PW [test-assertions](https://playwright.dev/docs/test-assertions), PW [best-practices](https://playwright.dev/docs/best-practices).

### C2. Test without assertions — 🔴
Clicks/fills but verifies nothing → green even when the feature is broken. Caught by the `expect-expect` rule. **Caveat:** if the project config adds POM methods (`check*`/`expect*`) to `assertFunctionNames`, a test that only calls `await page.checkX()` passes the rule — make sure such a method actually contains a web-first assertion and isn't empty.
Source: PW [best-practices](https://playwright.dev/docs/best-practices).

### C3. `expect.soft` for a block of checks — 🟡
Several independent checks of one section — use soft, to see all failures at once instead of just the first.
```ts
await expect.soft(card).toBeVisible();
await expect.soft(card.getByRole('heading')).toHaveText(/Plan/);
await expect.soft(card.getByRole('button')).toBeEnabled();
```
Source: PW [best-practices#use-soft-assertions](https://playwright.dev/docs/best-practices).

### C4. Brittle exact values — 🟠
```ts
// ❌
await expect(price).toHaveText('$4,567');
// ✅
await expect(price).toHaveText(/\$[\d,]+/);
```
Exact prices/dates/dynamic numbers change with no functional change — the test fails on live content, not on a bug.

### C5. `test.fail` vs `test.fixme` for a known bug — 🟡
`fixme` doesn't run → won't report the fix. `fail` runs, fails on the bug, and shouts "unexpectedly passed" once it's fixed.
```ts
// ✅ — the fail test contains ONLY the bug assertion; working behavior goes in a separate regular test
test.fail('BUG-123: total is not recalculated when the region changes', async ({ page }) => {
  await expect(total).toHaveText('recalculated');
});
```
Source: PW [test-annotations](https://playwright.dev/docs/test-annotations).

---

## D. Isolation and independence

### D1. Shared mutable state — 🔴/🟠
```ts
// ❌
let orderId;
test('create', async () => { orderId = ...; });
test('open', async () => { await page.goto(`/orders/${orderId}`); }); // fails when run alone / in a different order

// ✅ — each test is self-sufficient; shared setup goes in a fixture/beforeEach
test('open', async ({ request, page }) => {
  const { id } = await (await request.post('/api/orders', { data: {...} })).json();
  await page.goto(`/orders/${id}`);
});
```
Source: PW [best-practices#make-tests-isolated](https://playwright.dev/docs/best-practices).

### D2. `serial` without need — 🟠
`describe.configure({ mode: 'serial' })` disables isolation: the first failure takes down the rest. Only for a genuine dependency.
Source: PW [test-retries#serial-mode](https://playwright.dev/docs/test-retries).

### D3. Testing third-party — 🟠
External sites/widgets are unstable and out of your control.
```ts
// ❌ — navigating deep into an external service
await externalLink.click();
await expect(page).toHaveURL('https://account.example.com/dashboard');

// ✅ — oracle: the fact of an initiated navigation request to the target origin + abort
const reqPromise = page.waitForRequest(r => r.isNavigationRequest() && r.url().includes('account.example.com'));
await page.route('**account.example.com**', r => r.abort());
await externalLink.click();
await reqPromise;
```
Source: PW [best-practices#avoid-testing-third-party-dependencies](https://playwright.dev/docs/best-practices).

---

## E. TypeScript and lint

### E1. `any` — 🟠 in POM/utils · deliberate exceptions possible in specs
Typical setup: `@typescript-eslint/no-explicit-any` = `warn`, relaxed for `*.spec.ts` (mock data). Check against the project config — where `any` is deliberately allowed, don't flag it. Where it isn't:
```ts
// ❌ (POM/utils)
const data: any = await res.json();
// ✅
interface ArticlesResponse { items: { id: string }[] }
const data = (await res.json()) as ArticlesResponse;
expect(data.items).toHaveLength(3);
```
POM fields — `readonly Locator`; fixtures — `base.extend<{ featurePage: FeaturePage }>`; parameters — `Route`/`Request`.
Source: PW [test-typescript](https://playwright.dev/docs/test-typescript).

### E2. `@ts-ignore` / error suppression — 🟠
Hides a real type error. Only `@ts-expect-error` with a comment and a ticket is acceptable.
Source: PW [best-practices#lint-your-tests](https://playwright.dev/docs/best-practices).

### E3. Module system and import style — 🟡
Check against the project's actual code, not your own habits: ESM vs CJS (`"type": "module"` in `package.json`); relative paths vs tsconfig aliases (aliases may be declared but unused — don't impose them then); whether `import type` is enforced (`verbatimModuleSyntax`). Read the tsconfig and 2–3 neighboring files — follow the existing style. Remove unused imports/variables.
Source: PW [test-typescript](https://playwright.dev/docs/test-typescript).

---

## F. Network and mocks

### F1. Mocking the happy path instead of edges — 🟠
Mocking the main flow = the test verifies the mock, not the app. Mocks only for 5xx/empty/timeout/offline.
```ts
// ❌ — the positive flow is mocked
await page.route('**/api/products', r => r.fulfill({ json: PRODUCTS }));

// ✅ — positive flow against the real API; mock only for the error
await page.route('**/api/products', r => r.fulfill({ status: 500, body: '{}' }));
```
Source: PW [mock](https://playwright.dev/docs/mock), PW [best-practices](https://playwright.dev/docs/best-practices).

### F2. Form payload verification — 🟠
Don't stop at "the button is enabled" — inspect the request body.
```ts
const reqPromise = page.waitForRequest(r => r.url().includes('/api/feedback'));
await submit();
const body = (await reqPromise).postDataJSON();
expect(body).toMatchObject({ email: 'a@b.c', message: expect.any(String) });
expect(JSON.stringify(body)).not.toContain('[object Object]');  // common serialization bug
```
Client-side validation can be green while serialization is broken — the real contract is only visible in the payload.

### F3. Route after the action / global route — 🟠
Set up `page.route` **before** the trigger; scope it to the test/fixture, not the whole suite (otherwise it leaks into other tests).

---

## G. Structure, readability, hygiene

### G1. `test.step` by business steps — 🟡
```ts
await test.step('Fill the form', async () => {
  await page.getByLabel('Email').fill('a@b.c');
  await page.getByLabel('Name').fill('John');
});
await test.step('Submit', async () => {
  await page.getByRole('button', { name: 'Submit' }).click();
});
```
Name in the imperative; don't split into a step per action. `return` goes outside the callback. Steps show up in the HTML report/trace/Allure.
Source: PW [test.step](https://playwright.dev/docs/api/class-test#test-step).

### G2. Inline comments — 🟡
Tests self-document through names, semantic locators, and steps. Remove `// Step N:` in favor of `test.step`. Context goes into the reporter description/annotation (e.g. `allure.description`) if the project uses them.

### G3. Test copies instead of parameterization — 🟡
```ts
// ✅ — for...of OUTSIDE describe
for (const { region, expected } of REGIONS) {
  test(`Plan for ${region}`, async ({ page }) => { ... });
}
```
Source: PW [test-parameterize](https://playwright.dev/docs/test-parameterize).

### G4. Junk — 🔴/🟡
`test.only` (🔴, caught by `no-focused-test`), `page.pause()` (🔴), commented-out tests, `console.log`, temporary files, unused POM constants/methods (🟡).
Source: PW [best-practices#lint-your-tests](https://playwright.dev/docs/best-practices).

---

## H. Bug masking and flakiness

### H1. Synthetic UI bypasses — 🔴
`{ force: true }`, `dispatchEvent`, direct setters, manual scrolling instead of actionability — skip the visibility/actionability checks and hide a real bug. Caught by `no-force-option`.
```ts
// ❌
await page.locator('#submit').dispatchEvent('click');
await page.getByRole('button').click({ force: true });

// ✅
await page.getByRole('button', { name: 'Submit' }).click();   // auto-actionability
```
Exception — a genuinely non-standard controlled input (e.g. a custom `display:none` file input): first verify the behavior in a live browser, document the reason. Any bypass must **catch a regression** if the feature breaks, not silence it.
Source: PW [best-practices](https://playwright.dev/docs/best-practices), PW [actionability](https://playwright.dev/docs/actionability).

### H2. Retries as a cure — 🟠
A pass on retry = flakiness. Fix the cause (races/hydration/web-first waits), verify with `--retries=0 --repeat-each=5`. `configure({ retries })` — only as temporary quarantine with a ticket link.
Source: PW [test-retries](https://playwright.dev/docs/test-retries).

### H3. `try/catch` around actions — 🟠
Silences a failing action/assertion; auto-waiting is already built in, `.catch()` hides the bug.

### H4. Pre-release test behind skip/flag — 🟠
A test written before the feature ships must fail honestly, not hide behind `skip`/a feature flag: a hidden test will report neither the feature going live nor it breaking.

---

## I. Special cases by test type

### I1. API — 🟠
Check status AND body; request identifiers — a fresh `randomUUID()` from the built-in `node:crypto` per request (don't reuse across requests; don't pull in the `uuid` package if the project doesn't have it). Account for rate limits (unique email/phone, pauses); clean up created data via `afterEach`/teardown (write-only API without delete — leave a note).
```ts
import { randomUUID } from 'crypto';

test('POST /api/feedback validates email', async ({ request }) => {
  const res = await request.post('/api/feedback', { data: { requestId: randomUUID(), email: 'invalid', message: 'hi' } });
  expect(res.status()).toBe(400);
  expect(await res.json()).toMatchObject({ error: expect.any(String) });
});
```
Source: PW [api-testing](https://playwright.dev/docs/api-testing).

### I2. iframe / new tab / download / upload / time / permissions — 🟠
```ts
const frame = page.frameLocator('iframe[name="payment"]');         // iframe
const popup = await page.context().waitForEvent('page');           // new tab (promise before the click)
const download = await page.waitForEvent('download');              // download (promise before the click)
await page.getByLabel('Attach').setInputFiles('fixtures/doc.pdf'); // upload
await page.clock.install({ time: new Date('2026-01-01') });        // time
await context.grantPermissions(['geolocation']);                   // permissions
```
Manual bypasses of these APIs (e.g. calling a handler directly instead of waiting for the event) = 🟠.
Source: PW [frames](https://playwright.dev/docs/frames), [pages#handling-new-pages](https://playwright.dev/docs/pages), [downloads](https://playwright.dev/docs/downloads), [clock](https://playwright.dev/docs/clock).

### I3. visual regression — 🟠
```ts
await expect(card).toHaveScreenshot('card.png', {
  maxDiffPixelRatio: 0.01,
  animations: 'disabled',
  mask: [card.locator('.price'), card.locator('.banner')],
});
```
Generate baselines on the CI platform (a macOS baseline against Linux CI = guaranteed diff). Only when the test case requires a baseline and the team is ready to maintain snapshots.
Source: PW [test-snapshots](https://playwright.dev/docs/test-snapshots).

---

## J. Intent alignment

### J1. Surrogate oracle — 🟠
The test must verify what its name promises, not an indirect signal.
```ts
// ❌ — "form validation", but only the button's enabled state is checked
await expect(submitButton).toBeEnabled();

// ✅ — actually verify the submit result/payload
const reqPromise = page.waitForRequest('**/api/submit');
await submitButton.click();
expect((await reqPromise).postDataJSON()).toMatchObject({ ... });
```

### J2. Structural anchoring instead of exact content — 🟠
A post-fix regression test fails on the root symptom and checks structurally (presence, `count > 0`, regex) rather than specific texts/numbers — it survives content changes.

### J3. Oracle adapted to environment constraints — 🟠
Where the UI doesn't distinguish 404/5xx (one stub page for both) — assert at the network level, not "saw the error text". Where an environment with anti-bot protection kills browser XHRs (random 4xx on direct requests) — use `page.request` for API checks, not a form submit through the UI.

---

## K. Your project's rules — sample fill-in

> Template section: below is a fictional project so the format is visible (rule → violation → fix). Replace the content with your repository's conventions; source — its `CLAUDE.md` and existing code.

### K1. Custom fixture instead of the base `test` — 🟠
```ts
// ❌
import { test, expect } from '@playwright/test';   // loses the project's networkGuard fixture

// ✅
import { test, expect } from './fixtures/custom-test';
// …at the end of the test (or a single afterEach per spec):
networkGuard.expectNoErrors();
```
If the project provides a custom fixture (network error monitor, auto-dismissing banners, preconfigured POMs) — importing past it silently disables those guarantees. Document which import is required in which directories and which checks must be called.

### K2. Suite patterns — 🟠
Document the differences between suites (smoke / regress / api etc.): POM via fixtures or composition (`new XPage(page)` in `beforeEach`), reporter conventions (runtime API vs reporter-only, test ID format), testMatch/testIgnore, which file/describe new tests go into.

### K3. Environments — 🟠
POMs and tests are verified on all target environments, not just one: a test environment's DOM may differ from production (different heading levels, different footer markup, auth elements). Keep known environment quirks as a list next to this rule.

### K4. Skipped hygiene — 🟡
A test must not add permanent skipped entries to regular runs. Environment-specific tests are excluded via config (`testIgnore`/`testMatch`, moving to a separate spec if needed); runtime `test.skip` — only for dynamic conditions (feature flag, known bug with a ticket). Run outcome: passed = OK, failed = a problem, skipped = needs an explanation.

### K5. Dependencies and config — 🔴 if touched without being asked
Don't bump the `@playwright/test` version or add dependencies without checking against CI (Docker image, lock file); don't touch `playwright.config.ts` unless necessary; don't commit `.env`/secrets.
