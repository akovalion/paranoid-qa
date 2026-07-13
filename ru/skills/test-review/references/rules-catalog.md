# Каталог правил ревью — `❌ до → ✅ после`

Справочник к чеклисту `SKILL.md`. Каждое правило: severity, как выглядит нарушение, как чинить, почему. Категории A–K совпадают с чеклистом.

**Источники:** правила с пометкой **PW** подкреплены официальной документацией Playwright (`playwright.dev/docs/...`) — ссылка у правила. Остальные — инженерная практика, обоснование в тексте правила. Категория K — конвенции вашего проекта (источник — его `CLAUDE.md` и код).

---

## A. Детерминизм, ожидания, асинхронность

### A1. `waitForTimeout` и in-page паузы — 🔴
Слепая пауза = одновременно медленно и флак (на CI элемент может появиться позже).
```ts
// ❌
await page.click('button');
await page.waitForTimeout(2000);
expect(await page.locator('.result').count()).toBe(3);

// ✅
await page.getByRole('button', { name: 'Показать' }).click();
await expect(page.getByRole('listitem')).toHaveCount(3);
```
Грепать не только `page.waitForTimeout`, но и `setTimeout`/`sleep` внутри `page.evaluate(...)` — прячется там же.
Источник: PW [best-practices#use-web-first-assertions](https://playwright.dev/docs/best-practices).

### A2. Пропущенный `await` (floating promise) — 🔴
Промис не ожидается → тест продолжается до завершения действия/ассерта → недетерминированно «иногда проходит».
```ts
// ❌
expect(page.getByText('Готово')).toBeVisible();   // не дождётся
test.step('Отправить', async () => { ... });       // шаг не выполнится синхронно

// ✅
await expect(page.getByText('Готово')).toBeVisible();
await test.step('Отправить', async () => { ... });
```
**Важно:** без eslint-plugin-playwright линт floating promise не увидит (`valid-expect` ловит лишь часть форм). С подключённым recommended `missing-playwright-await` — уже error и ловится; зато `no-wait-for-timeout`, `no-force-option` и `expect-expect` там только warn (сверено по v2.10.5) — без `--max-warnings 0` они не валят CI, предложи поднять до error. `@typescript-eslint/no-floating-promises` требует type-aware линтинга. Нет нужных правил — **перечитывай глазами**.
Источник: PW [best-practices#lint-your-tests](https://playwright.dev/docs/best-practices).

### A3. Гонка в ожидании сети — 🔴
Объявление `waitForResponse`/`waitForRequest` **после** действия теряет событие.
```ts
// ❌
await page.getByRole('button', { name: 'Отправить' }).click();
const res = await page.waitForResponse('**/api/submit');  // клик мог уже отстреляться

// ✅
const resPromise = page.waitForResponse(r => r.url().includes('/api/submit') && r.request().method() === 'POST');
await page.getByRole('button', { name: 'Отправить' }).click();
const res = await resPromise;
```
Источник: PW [events#waiting-for-event](https://playwright.dev/docs/events).

### A4. `networkidle` и лишний `waitForLoadState` — 🟠
`networkidle` ненадёжен на тяжёлых SPA (постоянные фоновые запросы) и объявлен discouraged в доке.
```ts
// ❌
await page.goto('/checkout');
await page.waitForLoadState('networkidle');

// ✅
await page.goto('/checkout', { waitUntil: 'domcontentloaded' });
// дальше — web-first ожидание нужного элемента, без дублирующего waitForLoadState
```
Проверь, включён ли `no-networkidle` в конфиге проекта — если нет, линт не ловит, проверяй глазами.
Источник: PW [navigations](https://playwright.dev/docs/navigations).

### A5. Мгновенный замер как gate вместо `toPass` — 🟠
`count()`/`allTextContents()`/`isVisible()` не ретраятся → ловят промежуточное состояние (ре-рендер, гидратация).
```ts
// ❌
const items = await page.getByRole('listitem').allTextContents();
expect(items.length).toBeGreaterThan(5);

// ✅ — составную/производную проверку оборачиваем в toPass
await expect(async () => {
  const items = await page.getByRole('listitem').allTextContents();
  expect(items.length).toBeGreaterThan(5);
  expect(items.every(t => t.trim())).toBe(true);
}).toPass({ timeout: 10_000 });
// либо одиночное условие — обычным web-first:
await expect(page.getByRole('listitem')).toHaveCount(12);
```
Собирать данные через `count()`/`allTextContents()` можно — но **после** web-first ожидания стабильности, не сразу после появления.
Источник: PW [test-assertions#expecttopass](https://playwright.dev/docs/test-assertions).

### A6. SSR/гидратация (Nuxt/Next/аналоги) — 🟠
SSR-приложение может перемонтировать контент при гидратации → коллекция, видимая в HTML сразу, на миг пустеет и рендерится заново.
```ts
// ❌ — замер сразу после появления контейнера ловит окно пустоты
await form.waitFor();
const fields = await form.getByRole('textbox').count();   // может быть 0

// ✅
await expect(async () => {
  expect(await form.getByRole('textbox').count()).toBe(4);
}).toPass();
```
Частая ловушка на лендингах и формах SSR-фреймворков; см. также A5.

---

## B. Локаторы

### B1. Приоритет локаторов — 🟠 при CSS/XPath без причины
Официальный порядок: `getByRole({ name })` → `getByText` → `getByLabel` → `getByPlaceholder` → `getByAltText` → `getByTitle` → `getByTestId` → CSS (крайний случай) → XPath (почти никогда).
```ts
// ❌
page.locator('button.buttonIcon.episode-actions-later');
page.locator('div.card > div.body > span.title');

// ✅
page.getByRole('button', { name: 'Отправить' });
page.getByRole('listitem').filter({ hasText: 'Доставка' }).getByRole('heading');
```
CSS/XPath привязаны к структуре DOM и ломаются при ребрендинге; role-локаторы отражают то, как страницу воспринимают пользователь и AT.
Источник: PW [locators](https://playwright.dev/docs/locators), PW [best-practices#use-locators](https://playwright.dev/docs/best-practices).

### B2. Strict mode и `.nth()` — 🟡
Локатор должен резолвиться в один элемент; позиционный выбор хрупок (страница изменилась → другой элемент).
```ts
// ❌
page.getByRole('listitem').nth(2);

// ✅
page.getByRole('listitem').filter({ hasText: 'Премиум' });
page.getByRole('row', { name: 'Иванов' }).getByRole('button', { name: 'Удалить' });
```
`.nth()`/`.first()`/`.last()` — только когда элемент действительно нельзя выделить по смыслу, с комментарием-обоснованием.
Источник: PW [locators#strictness](https://playwright.dev/docs/locators).

### B3. Плавающие элементы — глобально от `page` — 🟠
Дропдауны, тосты, модалки, портальный контент, iframe часто рендерятся вне исходной секции (в конце `body`).
```ts
// ❌ — внутри секции дропдаун не найдётся
section.getByRole('option', { name: 'Москва' });

// ✅
page.getByRole('option', { name: 'Москва' });
```

### B4. Длинный текст как якорь — 🟡
`getByText('целое предложение подзаголовка')` ломается при правке копирайта.
```ts
// ❌
page.getByText('Оформите подписку онлайн за 5 минут без визита в офис');
// ✅
page.getByRole('heading', { name: /подписк/i });
```

---

## C. Ассерты

### C1. Web-first вместо ручных — 🔴/🟠
`isVisible()`/`count()` возвращают мгновенно и не ретраятся.
```ts
// ❌
expect(await page.getByText('Добро пожаловать').isVisible()).toBe(true);  // 🔴 (флак)
expect(await loc.count()).toBe(3);                                         // 🟠

// ✅
await expect(page.getByText('Добро пожаловать')).toBeVisible();
await expect(loc).toHaveCount(3);
```
Web-first (авто-ретрай до timeout): `toBeVisible/toHaveText/toContainText/toHaveCount/toHaveValue/toBeChecked/toBeEnabled/toBeDisabled/toHaveAttribute/toHaveClass/toHaveURL`. Проверь конфиг: если `prefer-web-first-assertions` не включено — линт ручные ассерты не ловит, проверяй глазами.
Источник: PW [test-assertions](https://playwright.dev/docs/test-assertions), PW [best-practices](https://playwright.dev/docs/best-practices).

### C2. Тест без ассертов — 🔴
Кликает/заполняет, но ничего не проверяет → зелёный, даже если функция сломана. Ловится правилом `expect-expect`. **Нюанс:** если конфиг проекта добавляет методы POM (`check*`/`expect*`) в `assertFunctionNames`, тест, вызывающий только `await page.checkX()`, правило проходит — убедись, что такой метод реально содержит web-first ассерт, а не пустой.
Источник: PW [best-practices](https://playwright.dev/docs/best-practices).

### C3. `expect.soft` для блока проверок — 🟡
Несколько независимых проверок одной секции — soft, чтобы увидеть все падения сразу, а не первое.
```ts
await expect.soft(card).toBeVisible();
await expect.soft(card.getByRole('heading')).toHaveText(/Тариф/);
await expect.soft(card.getByRole('button')).toBeEnabled();
```
Источник: PW [best-practices#use-soft-assertions](https://playwright.dev/docs/best-practices).

### C4. Хрупкие точные значения — 🟠
```ts
// ❌
await expect(price).toHaveText('4 567 ₽');
// ✅
await expect(price).toHaveText(/\d[\d\s]*₽/);
```
Точные цены/даты/динамические числа меняются без изменения функциональности — тест падает на живом контенте, а не на баге.

### C5. `test.fail` vs `test.fixme` для известного бага — 🟡
`fixme` не гоняется → не сообщит о починке. `fail` гоняется, падает на баге, кричит «unexpectedly passed» после фикса.
```ts
// ✅ — в fail-тесте ТОЛЬКО баг-ассерт; рабочее поведение — отдельным обычным тестом
test.fail('BUG-123: сумма не пересчитывается при смене региона', async ({ page }) => {
  await expect(total).toHaveText('пересчитано');
});
```
Источник: PW [test-annotations](https://playwright.dev/docs/test-annotations).

---

## D. Изоляция и независимость

### D1. Общий изменяемый state — 🔴/🟠
```ts
// ❌
let orderId;
test('создать', async () => { orderId = ...; });
test('открыть', async () => { await page.goto(`/orders/${orderId}`); }); // упадёт в одиночку/в другом порядке

// ✅ — каждый тест самодостаточен; общий setup — фикстура/beforeEach
test('открыть', async ({ request, page }) => {
  const { id } = await (await request.post('/api/orders', { data: {...} })).json();
  await page.goto(`/orders/${id}`);
});
```
Источник: PW [best-practices#make-tests-isolated](https://playwright.dev/docs/best-practices).

### D2. `serial` без необходимости — 🟠
`describe.configure({ mode: 'serial' })` отключает изоляцию: падение первого роняет остальные. Только при реальной зависимости.
Источник: PW [test-retries#serial-mode](https://playwright.dev/docs/test-retries).

### D3. Тестирование third-party — 🟠
Внешние сайты/виджеты нестабильны и вне контроля.
```ts
// ❌ — переход на внешний сервис «вглубь»
await externalLink.click();
await expect(page).toHaveURL('https://account.example.com/dashboard');

// ✅ — оракул: факт инициированного навигационного запроса нужного origin + abort
const reqPromise = page.waitForRequest(r => r.isNavigationRequest() && r.url().includes('account.example.com'));
await page.route('**account.example.com**', r => r.abort());
await externalLink.click();
await reqPromise;
```
Источник: PW [best-practices#avoid-testing-third-party-dependencies](https://playwright.dev/docs/best-practices).

---

## E. TypeScript и линт

### E1. `any` — 🟠 в POM/utils · возможны осознанные исключения в спеках
Типовая настройка: `@typescript-eslint/no-explicit-any` = `warn`, с послаблением для `*.spec.ts` (мок-данные). Сверь с конфигом проекта — где `any` разрешён осознанно, не флагай. Где не разрешён:
```ts
// ❌ (POM/utils)
const data: any = await res.json();
// ✅
interface ArticlesResponse { items: { id: string }[] }
const data = (await res.json()) as ArticlesResponse;
expect(data.items).toHaveLength(3);
```
Поля POM — `readonly Locator`; фикстуры — `base.extend<{ featurePage: FeaturePage }>`; параметры — `Route`/`Request`.
Источник: PW [test-typescript](https://playwright.dev/docs/test-typescript).

### E2. `@ts-ignore` / подавление ошибок — 🟠
Скрывает реальную ошибку типов. Допустимо только `@ts-expect-error` с комментарием и тикетом.
Источник: PW [best-practices#lint-your-tests](https://playwright.dev/docs/best-practices).

### E3. Модульная система и стиль импортов — 🟡
Сверь с фактическим кодом проекта, а не со своими привычками: ESM vs CJS (`"type": "module"` в `package.json`); относительные пути vs алиасы из tsconfig (алиасы могут быть объявлены, но не использоваться — тогда не навязывай их); форсится ли `import type` (`verbatimModuleSyntax`). Прочитай tsconfig и 2–3 соседних файла — следуй существующему стилю. Неиспользуемые импорты/переменные убрать.
Источник: PW [test-typescript](https://playwright.dev/docs/test-typescript).

---

## F. Сеть и моки

### F1. Мок happy-path вместо edge — 🟠
Мок основного сценария = тест проверяет мок, а не приложение. Моки только для 5xx/пусто/таймаут/офлайн.
```ts
// ❌ — позитивный сценарий замокан
await page.route('**/api/products', r => r.fulfill({ json: PRODUCTS }));

// ✅ — позитив против реального API; мок только для ошибки
await page.route('**/api/products', r => r.fulfill({ status: 500, body: '{}' }));
```
Источник: PW [mock](https://playwright.dev/docs/mock), PW [best-practices](https://playwright.dev/docs/best-practices).

### F2. Проверка payload формы — 🟠
Не останавливаться на «кнопка активна» — инспектировать тело запроса.
```ts
const reqPromise = page.waitForRequest(r => r.url().includes('/api/feedback'));
await submit();
const body = (await reqPromise).postDataJSON();
expect(body).toMatchObject({ email: 'a@b.c', message: expect.any(String) });
expect(JSON.stringify(body)).not.toContain('[object Object]');  // частая ошибка сериализации
```
Клиентская валидация может быть зелёной при сломанной сериализации — реальный контракт видно только в payload.

### F3. Роут после действия / глобальный роут — 🟠
`page.route` поставить **до** триггера; область — тест/фикстура, не весь suite (иначе протечёт в другие тесты).

---

## G. Структура, читаемость, гигиена

### G1. `test.step` по бизнес-шагам — 🟡
```ts
await test.step('Заполнить форму', async () => {
  await page.getByLabel('Email').fill('a@b.c');
  await page.getByLabel('Имя').fill('Иван');
});
await test.step('Отправить', async () => {
  await page.getByRole('button', { name: 'Отправить' }).click();
});
```
Имя — в императиве, не дробить на каждое действие. `return` — снаружи коллбэка. Шаги видны в HTML-репорте/trace/Allure.
Источник: PW [test.step](https://playwright.dev/docs/api/class-test#test-step).

### G2. Инлайн-комментарии — 🟡
Тесты самодокументируются именами, semantic-локаторами и шагами. Удалять `// Шаг N:` в пользу `test.step`. Контекст — в описании/аннотации репортера (напр. `allure.description`), если проект их использует.

### G3. Копии теста вместо параметризации — 🟡
```ts
// ✅ — for...of СНАРУЖИ describe
for (const { region, expected } of REGIONS) {
  test(`Тариф для ${region}`, async ({ page }) => { ... });
}
```
Источник: PW [test-parameterize](https://playwright.dev/docs/test-parameterize).

### G4. Мусор — 🔴/🟡
`test.only` (🔴, ловится `no-focused-test`), `page.pause()` (🔴), закомментированные тесты, `console.log`, временные файлы, неиспользуемые константы/методы POM (🟡).
Источник: PW [best-practices#lint-your-tests](https://playwright.dev/docs/best-practices).

---

## H. Маскировка багов и флак

### H1. Синтетические обходы UI — 🔴
`{ force: true }`, `dispatchEvent`, прямой setter, ручной скролл вместо actionability — пропускают проверки видимости/доступности и прячут реальный баг. Ловится `no-force-option`.
```ts
// ❌
await page.locator('#submit').dispatchEvent('click');
await page.getByRole('button').click({ force: true });

// ✅
await page.getByRole('button', { name: 'Отправить' }).click();   // auto-actionability
```
Исключение — действительно нестандартный контролируемый input (напр. кастомный `display:none` file-инпут): сперва проверь поведение в живом браузере, задокументируй причину. Любой обход должен **ловить регрессию**, если фича сломается, а не глушить её.
Источник: PW [best-practices](https://playwright.dev/docs/best-practices), PW [actionability](https://playwright.dev/docs/actionability).

### H2. Retries как лекарство — 🟠
Pass-на-ретрае = флак. Чинить причину (гонки/гидратация/web-first ожидания), верифицировать `--retries=0 --repeat-each=5`. `configure({ retries })` — только временный карантин со ссылкой на тикет.
Источник: PW [test-retries](https://playwright.dev/docs/test-retries).

### H3. `try/catch` вокруг действий — 🟠
Глушит падение действия/ассерта; auto-waiting уже встроен, `.catch()` прячет баг.

### H4. Пред-релизный тест за skip/флагом — 🟠
Тест, написанный до выката фичи, должен падать честно, не прятаться за `skip`/фиче-флагом: спрятанный тест не сообщит ни о выкате фичи, ни о её поломке.

---

## I. Спецслучаи по типу теста

### I1. API — 🟠
Проверять статус И тело; идентификаторы запросов — свежий `randomUUID()` из встроенного `node:crypto` на каждый запрос (не переиспользовать между запросами; не тащи пакет `uuid`, если его нет в проекте). Учитывать rate limit (уникальные email/phone, паузы); cleanup созданного через `afterEach`/teardown (write-only API без delete — оставить пометку).
```ts
import { randomUUID } from 'crypto';

test('POST /api/feedback валидирует email', async ({ request }) => {
  const res = await request.post('/api/feedback', { data: { requestId: randomUUID(), email: 'invalid', message: 'hi' } });
  expect(res.status()).toBe(400);
  expect(await res.json()).toMatchObject({ error: expect.any(String) });
});
```
Источник: PW [api-testing](https://playwright.dev/docs/api-testing).

### I2. iframe / новый таб / download / upload / время / права — 🟠
```ts
const frame = page.frameLocator('iframe[name="payment"]');         // iframe
const popup = await page.context().waitForEvent('page');           // новый таб (promise до клика)
const download = await page.waitForEvent('download');              // скачивание (promise до клика)
await page.getByLabel('Прикрепить').setInputFiles('fixtures/doc.pdf'); // загрузка
await page.clock.install({ time: new Date('2026-01-01') });        // время
await context.grantPermissions(['geolocation']);                   // права
```
Ручные обходы этих API (например, прямой вызов хэндлера вместо ожидания события) = 🟠.
Источник: PW [frames](https://playwright.dev/docs/frames), [pages#handling-new-pages](https://playwright.dev/docs/pages), [downloads](https://playwright.dev/docs/downloads), [clock](https://playwright.dev/docs/clock).

### I3. visual regression — 🟠
```ts
await expect(card).toHaveScreenshot('card.png', {
  maxDiffPixelRatio: 0.01,
  animations: 'disabled',
  mask: [card.locator('.price'), card.locator('.banner')],
});
```
Эталоны генерировать на платформе CI (macOS-эталон против Linux-CI = гарантированный diff). Только если тест-кейс требует эталон и команда готова поддерживать снапшоты.
Источник: PW [test-snapshots](https://playwright.dev/docs/test-snapshots).

---

## J. Соответствие намерению

### J1. Суррогатный оракул — 🟠
Тест проверяет то, что обещает имя, а не косвенный признак.
```ts
// ❌ — «валидация формы», а проверяется только активность кнопки
await expect(submitButton).toBeEnabled();

// ✅ — реально проверяем результат сабмита/payload
const reqPromise = page.waitForRequest('**/api/submit');
await submitButton.click();
expect((await reqPromise).postDataJSON()).toMatchObject({ ... });
```

### J2. Структурная привязка к контенту — 🟠
Регресс после фикса падает на корневом симптоме и проверяет структурно (наличие, `count > 0`, regex), а не конкретные тексты/числа — переживёт смену контента.

### J3. Оракул под ограничение окружения — 🟠
Где UI не различает 404/5xx (одна заглушка на оба) — проверка сетевая, не «увидел текст ошибки». Где стенд с антибот-защитой режет браузерные XHR (случайные 4xx на прямые запросы) — для API-проверок `page.request`, не сабмит формы через UI.

---

## K. Правила вашего проекта — пример заполнения

> Раздел-шаблон: ниже вымышленный проект, чтобы был виден формат (правило → нарушение → фикс). Замените содержимое на конвенции своего репозитория; источник — его `CLAUDE.md` и существующий код.

### K1. Кастомная фикстура вместо базового `test` — 🟠
```ts
// ❌
import { test, expect } from '@playwright/test';   // теряется проектная фикстура networkGuard

// ✅
import { test, expect } from './fixtures/custom-test';
// …в конце теста (или один afterEach на спек):
networkGuard.expectNoErrors();
```
Если проект даёт кастомную фикстуру (монитор сетевых ошибок, авто-закрытие баннеров, преднастроенные POM) — импорт мимо неё молча отключает эти гарантии. Зафиксируйте: в каких директориях какой импорт обязателен и какие проверки должны вызываться.

### K2. Паттерны сьютов — 🟠
Зафиксируйте различия между сьютами (smoke / regress / api и т.п.): POM через фикстуры или композицию (`new XPage(page)` в `beforeEach`), конвенции репортера (runtime API vs reporter-only, формат ID тестов), testMatch/testIgnore, в какой файл/describe добавлять новые тесты.

### K3. Окружения — 🟠
POM и тесты проверены на всех целевых стендах, не только на одном: DOM тест-стенда может отличаться от прода (другие уровни заголовков, другая разметка футера, элементы авторизации). Известные особенности стендов держите списком рядом с этим правилом.

### K4. Skipped-гигиена — 🟡
Тест не добавляет постоянных skipped в штатные прогоны. Окружение-специфичное исключается конфигом (`testIgnore`/`testMatch`, при необходимости — вынос в отдельный spec); runtime `test.skip` — только для динамических условий (фича-флаг, известный баг с тикетом). Итог прогона: passed = ок, failed = проблема, skipped = требует объяснения.

### K5. Зависимости и конфиг — 🔴 если затронуто без запроса
Не бампать версию `@playwright/test`, не добавлять зависимости без сверки с CI (Docker-образ, lock-файл); не трогать `playwright.config.ts` без необходимости; не коммитить `.env`/секреты.
