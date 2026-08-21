# Промт для лендинга paranoid-qa
# Вставлять целиком в v0 / Lovable / Figma Make / Claude.
# Числа и тексты реальные, проверены; ничего не выдумывать сверх написанного.

Build a single-page landing site for **paranoid-qa** — an open-source pack of Claude Code skills that turns an AI coding agent into a meticulous QA engineer.

## Positioning & audience
Visitors are QA automation engineers and dev-tool early adopters arriving from GitHub, Hacker News, and tech articles. They are allergic to marketing. The page must read like it was made by an engineer for engineers: dry, specific, zero hype. The product is free and MIT-licensed. The only conversions are (1) GitHub star / install, and (2) an optional email waitlist for future team features.

## Core message
AI agents happily report "all tests pass" without proof. paranoid-qa forbids that: every Pass/Fail verdict must cite an observed artifact — tool output, screenshot, or network log. "Not tested" and "Blocked" are legitimate outcomes; a guess is not.

## Tech constraints
- Two static pages: `index.html` (EN, default) and `ru/index.html` (RU) + one shared CSS file. No frameworks, no build step (GitHub Pages hosting)
- Header has a minimal EN | RU switcher linking the two pages. No auto-redirect by browser language — annoying and breaks direct links
- `hreflang` alternate tags on both pages; OG meta tags localized per page
- Dark theme by default, light theme via `prefers-color-scheme`
- Responsive down to 375px; page weight under 150KB excluding the demo GIF
- Favicon: magnifying-glass motif
- All numbers and copy below are real — do NOT invent stats, testimonials, or customer logos

## Visual direction
- Terminal/CLI aesthetic: near-black background (#0d1117 family), JetBrains Mono for code and numbers, Inter or system sans for prose
- Accents: terminal green (#3fb950) for pass/proof, amber (#d29922) for warnings, red (#f85149) sparingly for fail states
- Flat, sharp, information-dense. No gradient blobs, no stock AI-brain art, no glassmorphism
- Micro-motion only: typing/caret animation in the hero terminal, subtle card hover. No parallax, no scroll-jacking

## Page structure and copy (use verbatim)

### 1. Hero
- Name: `paranoid-qa`
- H1: **Your AI agent says all tests pass. Prove it.**
- Sub: Claude Code skills that force an agent to test like a paranoid QA engineer: every verdict backed by an observed artifact — tool output, screenshot, or network log.
- Visual: embedded terminal window playing the real demo GIF (`assets/demo.gif` from the repo) — the agent catches a seeded `[object Object]` bug in a form payload
- Primary CTA: **View on GitHub** → https://github.com/akovalion/paranoid-qa
- Secondary: copyable install block:
  ```
  /plugin marketplace add akovalion/paranoid-qa
  /plugin install paranoid-qa
  ```
- Below CTAs: auto-updating shields.io badges (GitHub stars, MIT license)

### 2. Problem (3 lines max)
- H2: **Optimism is a bug in test automation**
- Copy: An LLM agent is trained to be helpful. Left alone, it clicks a button, sees no error, and reports success — while the API silently received `[object Object]` instead of your form data. Green checkmarks without evidence are worse than no tests: they buy false confidence.

### 3. How it works (3 numbered steps, terminal-styled)
1. **Install the pack** — one command, skills load into Claude Code
2. **Ask the agent to test** — it plans checks, drives the browser, watches the network
3. **Read a verdict you can audit** — every Pass cites an artifact; every gap is reported as "Not tested", not glossed over

### 4. What's inside (5 cards)
- **testing** — evidence-first execution framework: 935 individual checks across forms, payloads, responsive layouts and cross-browser quirks, plus a catalog of 26 checks agents most often skip
- **test-review** — 49-point review checklist and a 43-rule catalog for Playwright/TypeScript autotests, with severity levels and ready fixes
- **test-cases** — test-case generation that follows QA design techniques instead of improvising
- **bug-report** — reports with steps, expected/actual and environment, written from observed evidence only
- **interview** — structured requirement-gathering before any testing starts

Card footer note: English and Russian versions included.

### 5. Principles (styled as lint output / a config file)
```
✓ Evidence or it didn't happen
✓ "Not tested" is an honest answer. A guess is not
✓ Blocked ≠ Passed
✓ Retest after every fix — trust nothing, including yourself
```

### 6. Articles / proof
- Two article cards (Habr, RU): the evidence-discipline story and the lint-severity deep-dive (links provided at build time)
- GitHub stars badge repeated once

### 7. Waitlist (clearly separated optional block)
- H2: **Team features someday, maybe**
- Copy: Hosted run reports, team dashboards, CI integration — only if people actually want them. Leave an email and I'll ask you first.
- Single email field + button **Count me in** (Formspree/Tally endpoint — placeholder URL, mark as TODO)
- Honesty note under the field: *No newsletter. One email if this ships.*

### 8. Footer
MIT · built by Aleksei Kovalev (@akovalion) · GitHub · Habr

## Russian copy for `ru/index.html` (use verbatim)

Same eight sections, same layout. Typography: long dashes (—), «ёлочки» for quotes, consistent «ё».

### 1. Хиро
- H1: **Твой AI-агент говорит, что все тесты прошли. Пусть докажет.**
- Sub: Скиллы для Claude Code, которые заставляют агента тестировать как параноидальный QA-инженер: каждый вердикт подкреплён наблюдаемым артефактом — выводом инструмента, скриншотом или логом сети.
- CTA: **Смотреть на GitHub** (та же ссылка), блок установки без изменений
- Бейджи те же

### 2. Проблема
- H2: **Оптимизм — это баг в автоматизации тестирования**
- Текст: LLM-агент обучен быть полезным. Оставь его без присмотра — он кликнет по кнопке, не увидит ошибки и отчитается об успехе, пока API молча получает `[object Object]` вместо данных формы. Зелёные галочки без доказательств хуже, чем отсутствие тестов: они дают ложную уверенность.

### 3. Как это работает
1. **Поставь пак** — одна команда, скиллы подхватываются Claude Code
2. **Попроси агента протестировать** — он планирует проверки, водит браузер, следит за сетью
3. **Читай вердикт, который можно проверить** — каждый Pass ссылается на артефакт; каждый пробел помечен как «не проверено», а не замазан

### 4. Что внутри (5 карточек)
- **testing** — фреймворк доказательного прогона: 935 отдельных проверок по формам, payload, адаптиву и кросс-браузерным особенностям, плюс каталог из 26 проверок, которые агенты пропускают чаще всего
- **test-review** — чеклист ревью на 49 пунктов и каталог из 43 правил для автотестов Playwright/TypeScript, с severity и готовыми фиксами
- **test-cases** — генерация тест-кейсов по техникам тест-дизайна, а не по наитию
- **bug-report** — репорты со шагами, ожидаемым/фактическим и окружением — только из наблюдённых фактов
- **interview** — структурированный сбор требований до старта тестирования

Подпись под карточками: версии на английском и русском в комплекте.

### 5. Принципы (стилизовать как вывод линтера)
```
✓ Нет пруфа — не было проверки
✓ «Не проверено» — нормальный ответ. Догадка — нет
✓ Blocked ≠ Passed
✓ Ретест после каждого фикса — не верь никому, включая себя
```

### 6. Статьи / пруф
- Те же две карточки статей с Хабра (здесь они на родном языке аудитории — дать заголовки статей как есть)
- Бейдж со звёздами один раз

### 7. Waitlist
- H2: **Командные фичи. Когда-нибудь. Может быть**
- Текст: Хостинг отчётов, командные дашборды, интеграция с CI — только если это правда кому-то нужно. Оставь почту — спрошу тебя первым.
- Поле email + кнопка **Я в деле** (тот же endpoint-плейсхолдер, TODO)
- Приписка под полем: *Никакой рассылки. Одно письмо, если это выйдет.*

### 8. Футер
MIT · сделал Алексей Ковалёв (@akovalion) · GitHub · Хабр

## Hard rules
- Do not add sections beyond these eight
- Do not invent quotes, customer logos, usage numbers, or roadmap promises
- Total prose per page under ~350 words; when in doubt, cut
- Copy tone: engineer-dry with a hint of paranoid humor; never salesy
- EN and RU pages must stay content-identical section by section — no language-exclusive blocks
