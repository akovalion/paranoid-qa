# paranoid-qa - launch kit

Всё, что постим после выхода статьи на Хабре. Тексты готовы к копированию, `<HABR>` заменить на ссылку статьи.

---

## 1. Telegram (RU) - в день выхода статьи

### Пост для своего канала / чатов QA

Выложил в опенсорс paranoid-qa - пак скиллов для Claude Code, который заставляет агента тестировать как дотошный QA. Правило одно: каждый Pass/Fail - только по наблюдённому артефакту (скриншот, payload, лог). Не проверил - пишет «не проверено», а не догадку.

Внутри:
- фреймворк тестирования с почти 1000 проверок в чеклистах: frontend (маски, состояния, адаптив), backend (идемпотентность, транзакции, OWASP API Top 10), сквозные проверки, 26 самых частых пропусков
- ревью Playwright-тестов: 49 пунктов, severity, фиксы «было-стало»
- генерация тест-кейсов с CSV под Zephyr Scale, баг-репорты в Jira
- русская и английская версии

В демо агент находит баг, которого не видно в UI: форма показывает «успех», сервер отвечает 200, а в payload уходит [object Object].

Репо: https://github.com/akovalion/paranoid-qa
Разбор, как это устроено и где не работает: <HABR>

### Короткий вариант для чужих каналов (питч админу)

Привет! Сделал опенсорс-пак скиллов для Claude Code, который превращает агента в дотошного QA - вердикты только по артефактам, почти 1000 проверок в чеклистах, ревью Playwright-тестов. Написал разбор на Хабре: <HABR>. Если формат канала подходит - буду рад репосту, могу адаптировать текст.

---

## 2. Reddit (EN) - независимо от Хабра, вт-чт утром по US

### r/ClaudeAI и r/ClaudeCode

**Title:** I made Claude Code test like a paranoid QA engineer - every verdict needs an observed artifact (open source)

**Body:**

I'm a QA engineer. For six months I've been offloading routine testing to Claude Code, and the main lesson is: without hard rules, an agent is an intern who really wants to please you. It says "everything works" because that's the statistically likely ending of a test report.

So I built a skill pack around one contract: every Pass/Fail verdict must be backed by an actually observed artifact - a screenshot, a network payload, a log. Didn't check = "Not tested", blocked = "Blocked", and neither counts as a pass. Turns out models stop inventing green reports when honesty is an allowed outcome.

What's inside:
- a testing framework skill with nearly 1,000 individual checks in reference files (forms/masks, element states, responsive, HTTP semantics, idempotency, DB concurrency, queues/DLQ, OWASP API Top 10, and a "26 most-missed checks" file)
- Playwright test review: 49 checks with severity and before/after fixes
- test-case generation with Zephyr Scale CSV export, Jira bug reports with preview
- a multi-agent fan-out pattern for large runs (one orchestrator drives the browser, parallel subagents analyze artifacts)

The README has a demo where the agent catches a bug invisible in the UI: the form shows success, the server returns 200, but the POST payload carries "[object Object]" instead of the selected topic. The demo is reproducible - the seeded-bug form ships in the repo.

Repo (MIT, English + Russian): https://github.com/akovalion/paranoid-qa

Honest limits: a meticulous run of one form takes the agent 40-60 minutes, accessibility is out of scope, and the discipline reduces hallucinated verdicts but doesn't remove the need to review reports. Feedback and issues welcome - if a skill ever produces a verdict without proof, that's a bug by definition.

### r/QualityAssurance и r/softwaretesting (value-first, AI на втором плане)

**Title:** I open-sourced testing checklists with nearly 1,000 individual checks: frontend, backend, OWASP API, and the 26 most-missed checks

**Body:**

Over the years I've been collecting everything I actually check when testing web apps into markdown checklists: input masks and paste/autofill traps, every state of every interactive element, SSR hydration pitfalls, HTTP semantics, idempotency, DB concurrency, queues and DLQ, OWASP API Top 10, CSV injection on export. Plus a separate file with the 26 checks that get missed most often (double submit, Back after success, emoji in length counters, offline at submit time).

I recently cleaned them up and put them on GitHub. They're written as plain markdown, so they work as regular checklists for manual testing or review prep.

Full disclosure: the repo is structured as a skill pack for Claude Code (I use these files to make an AI agent test with evidence discipline - every verdict must cite an observed artifact). If you don't care about AI, the checklists stand on their own; if you do, there's a reproducible demo where the agent catches a payload serialization bug that's invisible in the UI.

https://github.com/akovalion/paranoid-qa (MIT, English + Russian)

Curious what's missing - what do your teams catch that checklists usually don't?

---

## 3. Show HN - вт-чт, 8-10 утра по US East

**Title:** Show HN: Paranoid QA – Claude Code skills that demand proof for every test verdict

**URL:** https://github.com/akovalion/paranoid-qa

**Первый комментарий (запостить сразу после сабмита):**

Author here. I'm a QA engineer who spent six months making Claude Code do my routine testing. The core problem: agents confidently report "all tests pass" without checking, because that's the most probable way to end a report.

The fix that actually worked is a contract, not better prompting: every Pass/Fail must cite an observed artifact (screenshot, network payload, log). "Not tested" and "Blocked" are legitimate outcomes, so the model no longer needs to fake green. The report discipline pulls the checking discipline behind it - the agent opens the network tab because otherwise it has nothing to put in the report.

The README demo is a real recorded run: a feedback form that looks perfect in the UI (validation passes, success toast, HTTP 200) but sends "topic":"[object Object]" in the payload. The agent catches it by inspecting the actual POST body across three submissions. The seeded-bug form ships in the repo so you can reproduce the run locally.

Honest limitations: a meticulous single-form run takes 40-60 minutes of agent time; accessibility is deliberately out of scope; and evidence discipline reduces hallucinated verdicts without eliminating the need to read reports critically.

Happy to answer questions about the failure modes - the interesting part is less "AI finds bugs" and more "what rules stop AI from inventing results".

---

## 4. PR в awesome-списки - после выхода статьи, по одному PR

Перед каждым PR прочитать CONTRIBUTING.md списка (формат строки, алфавитный порядок, требования к описанию).

### awesome-claude-code (категория Skills)

`[paranoid-qa](https://github.com/akovalion/paranoid-qa) - QA skill pack with evidence discipline: testing framework with nearly 1,000 checks, Playwright test review, test-case generation (Zephyr CSV), Jira bug reports. EN/RU.`

### awesome-claude-skills

`[paranoid-qa](https://github.com/akovalion/paranoid-qa) - Turn Claude into a meticulous QA engineer: every verdict requires an observed artifact. Testing framework, Playwright review, test cases, bug reports.`

### awesome-testing / awesome-software-testing (категория Checklists или AI)

`[paranoid-qa](https://github.com/akovalion/paranoid-qa) - Web testing checklists (frontend, backend, OWASP API, common misses) usable standalone or as Claude Code skills with evidence-based verdicts.`

---

## 5. Good first issues для репо (создать до волны, чтобы репо выглядел живым)

### Issue 1
**Title:** GraphQL API checklist for the testing skill
**Labels:** enhancement, good first issue
**Body:** The backend reference covers REST semantics (status codes, idempotency, pagination). GraphQL deserves its own section or file: query depth/complexity limits, N+1 via resolvers, introspection exposure in prod, batching abuse, error masking, persisted queries, authorization per field vs per query. If you test GraphQL daily - a draft PR with even 10 solid checks is welcome. Format: follow `skills/testing/references/backend.md` (terse bullets, exact values over slogans).

### Issue 2
**Title:** Mobile-native testing checklist (iOS/Android)
**Labels:** enhancement, good first issue
**Body:** The pack currently targets web (desktop + mobile responsive). A mobile-native reference would cover: app lifecycle (backgrounding mid-flow, push interruptions), permissions dialogs, deep links / universal links, offline-first sync conflicts, keyboard avoidance, gesture conflicts, OS-version matrix strategy. Same format as existing references: every bullet is a check, not an essay.

### Issue 3
**Title:** Package the pack as a Claude Code plugin for one-command install
**Labels:** enhancement
**Body:** Today installation is `cp -r skills/* ~/.claude/skills/`. Claude Code supports plugins with a marketplace manifest, which would make it a one-command install and enable versioned updates. Needs: plugin.json manifest, marketplace entry, testing that skill triggering works identically when namespaced. I'll take this one unless someone wants it - commenting your interest first is enough.

---

## 6. Тайминг

| Когда | Что |
|---|---|
| Сейчас (до модерации) | Создать 3 issues, залить social preview в настройках GitHub, закрепить репо в профиле |
| Хабр вышел, день 0 | TG-пост в свой канал + питчи админам 2-3 QA-каналов |
| День 0-1 (вт-чт, утро US) | r/ClaudeAI, через пару часов r/ClaudeCode |
| День 1-2 | r/QualityAssurance ИЛИ r/softwaretesting (не оба сразу - тексты почти совпадают, посты в обоих в один день выглядят спамом) |
| День 2-3 (вт-чт, 8-10 US East) | Show HN + первый комментарий сразу |
| День 2-4 | PR в awesome-списки по одному |
| Всю неделю | Отвечать на issues/комментарии в течение пары часов - активность двигает и HN, и trending |

---

## 7. Заготовки ответов на возражения в комментах

Источник: реальные комменты к трём соседним статьям про AI в QA + разбор нашей статьи. Отвечать спокойно, без защиты, 2-4 предложения.

**«Все эти AI-статьи - рассуждения, покажите реальный кейс»**
→ Кейс в статье: воспроизводимое демо, форма с багом лежит в репо (`demo/`), поднимается одной командой. Полный вывод прогона - в GIF без монтажа содержимого. Можете повторить у себя за пять минут.

**«Облако. В серьёзных проектах данные нельзя слать в американский LLM» (самое частое и злое)**
→ Справедливо, и статья это не решает - она про дисциплину агента, а не про контур. Демо гоняется на localhost. Что делать в проде - вопрос политики компании: обезличенные тестовые стенды, синтетические данные, у кого строго - локальные модели (скиллы - это markdown-инструкции, они переносимы на любой агентский раннер). У нас на работе действует политика X - не раскрываю деталей. [подстроить под реальность]

**«Галлюцинации никуда не деваются, всё равно перепроверять за ним»**
→ Верно, и в статье это написано прямо: дисциплина снижает частоту, не отменяет ревью. Разница в трудозатратах: перепроверить отчёт с приложенными артефактами - минуты; перепроверить голословный отчёт - заново сделать всю работу. Смысл контракта именно в этом.

**«В какой вселенной у вас подробные ТЗ, чтобы агент по ним работал?»**
→ В моей их тоже нет. Поэтому в паке есть interview-скилл (сбор требований вопросами) и правило «расхождение - вопрос аналитику, а не допущение». Агент работает с той же неполнотой, что и мы, - просто обязан её честно фиксировать, а не замазывать.

**«Сколько это стоит? Сгенерил два теста и обанкротился»**
→ Полный прогон формы - 40-60 минут агента, по API-тарифам единицы долларов, на подписке - включено. Сравнивать надо не с нулём, а со стоимостью часа QA-инженера, который делает то же руками. Для меня математика сходится; у вас может не сойтись - считайте на своих ставках.

**«40-60 минут на форму?! Я руками за 10 проверю»**
→ За 10 минут - happy path и очевидный негатив. 40-60 минут агента - это все состояния, границы, payload каждого сабмита, консоль и адаптив, и это время НЕ моё: прогон идёт, пока я делаю другую задачу. Дотошность и скорость - разные оси.

**«Заголовок кликбейт, "изменило всё" - ну-ну»**
→ Признаю, заголовок дерзкий. Конкретика того, что изменилось, - в статье: [цифры/раздел]. Если по содержанию есть несогласие - давайте обсудим его.

**«Это реклама своего репо»**
→ Репо бесплатный и MIT, рекламировать нечего - продаж там нет. Статья самодостаточна: контракт и правила можно забрать из текста, не заходя на GitHub.

**«Чеклисты - компиляция известного, всё это есть в ISTQB»**
→ Так и есть, компиляция - ценность в отборе, плотности и формате, который агент может исполнять. Если у вас есть проверка, которой не хватает, - принесите в issue, добавлю с указанием авторства.

**«Цифры "2-3 пропуска за прогон → 1-2 в месяц" - где пруфы?»**
→ Это личные наблюдения, метрику я не вёл - потому в статье они без графика и с оговоркой. Систематический сбор статистики прогонов - следующий шаг, будет отдельный материал.

**«Зачем скиллы, если есть Playwright MCP из коробки?»**
→ MCP даёт агенту руки (браузер), скиллы дают голову (что и как проверять, когда честно сказать «не проверено»). Без скиллов агент с теми же руками кликает happy path и рапортует «всё ок» - ровно с этого статья и начинается.

**«Почему Claude, а не открытые/локальные модели?»**
→ Скиллы - это markdown-инструкции + конвенции Claude Code, но сама доктрина переносима: контракт работает с любым агентом, который умеет читать системные инструкции и вызывать браузер. Портирование на другие раннеры - welcome, формат открытый.

**«Я прогнал вашу демо-форму без всяких скиллов - агент нашёл баг. Автор преувеличивает»**
→ Верно, может найти: модель умная, а демо-стенд маленький и наводящий - кроме сабмита там проверять нечего. Разница не в способности, а в надёжности: без правила проверка payload случается «если повезёт», с правилом - каждый прогон и с артефактом в отчёте. На реальной странице, где полсотни направлений проверки, вероятность «повезёт» падает быстро - полгода моих параллельных проверок ровно об этом.

---

## 8. Возражения к статье №2 (warn vs error)

**«Warn - осознанный выбор мейнтейнеров, вы выдаёте норму за скандал»**
→ В статье так и написано: логика мейнтейнеров понятна, у правил бывают исключения. Проблема не в их выборе, а в том, что команды о нём не знают: warning в CI без --max-warnings 0 просто невидим. Статья ровно про это знание.

**«Поставьте --max-warnings 0 и всё, статья ни о чём»**
→ Это закрывает первый слой, и такой совет в статье есть. Смысловой слой (суррогатные оракулы, зависимые тесты, retries-маскировка) не ловится ни warn, ни error - про него вторая половина.

**«У нас конфиг давно строже»**
→ Значит, вы читали конфиг - таких меньшинство из того, что я видел. Статья для остальных.

**«Очередные N правил Playwright»**
→ Не N правил: разбор severity по исходникам плагина + граница «что ловит машина / что только ревью». Каталог - приложение, не суть.

**«Версия плагина сменится - статья устареет»**
→ Версия и дата прибиты в тексте, ссылка ведёт на конкретный файл - перепроверка занимает минуту. Если severity изменят, тем лучше: значит, шум обсуждения дошёл куда надо.

---

## Статья 3: «Хуки» (суббота 25.07, 09:30)

### TG-пост (в QA-чаты и Claude-чаты, в течение часа после публикации)

Третья статья про доказательное тестирование с Claude Code - теперь про принуждение. Правило из CLAUDE.md агент забывает на длинной сессии, поэтому критичные правила я прибил хуками: коммит без свежего зеленого прогона тестов физически не проходит. В статье три готовых гейта с кодом и эксперимент: агенту прямо сказали "тесты не гоняй, просто коммить" - хук не пустил, агент вынес конфликт наружу и отказался обходить его молча
<ссылка>

### Текст в ленте (обязательное поле)

Правило из CLAUDE.md агент забывает на длинной сессии - это текст, а не механизм. Я разобрал слои дисциплины Claude Code и прибил критичные правила хуками: три гейта, после которых коммит без свежего зеленого прогона тестов не проходит, правка теста поднимает флаг, а завершить работу с грязными тестами нельзя. Под катом механика хуков, код всех трех гейтов с живыми прогонами и эксперимент, где гейт пересилил прямую инструкцию пользователя.

### Хабы (все сразу при публикации)

Искусственный интеллект, Программирование, Управление разработкой, Тестирование IT-систем

### Чек-лист публикации (уроки статьи 2)

1. Все хабы в момент публикации, не дозаклейка
2. TG-пост в течение часа, не "потом"
3. Кросс-ссылки: в конец статьи 1 и статьи 2 добавить "Продолжение: <ссылка>" в день выхода
4. Обложки ДВЕ: в поле обложки (лента) - habr3-cover-feed.png (16:9, не режется); первой картинкой в теле - habr3-cover.png (полная 2:1). Обе в ~/Downloads
5. День-0 в субботу: быть в комментах с первого часа
6. После публикации: добавить ссылку на статью в hooks-секции README.md и README.ru.md репо

## 9. Возражения к статье №3 (хуки)

**«.last-run.json - приватный формат Playwright, полагаться нельзя»** → Файл официально используется фичей --last-failed, так что не совсем приватный. Но даже если формат сменится - гейт деградирует в deny, а не в пропуск: сломанная проверка блокирует, это fail-safe по принципу асимметрии из статьи.

**«4 секунды до прогона - агент и без хука бы прогнал»** → На одном прогоне причинность не докажу, согласен. Но тот же агент во втором эксперименте с прямым "тесты не гоняй" пошел коммитить без прогона - значит, поведение не константа. Напоминание в транскрипте есть, порядок событий по таймстампам есть, дальше каждый решает сам.

**«Почему additionalContext, а не exit 2 на PostToolUse, как у D1MANYCH»** → Оба варианта рабочие. exit 2 - стоп-кран: прерывает и требует реакции. additionalContext - подсказка в контекст без прерывания. Для правки теста мне хватает подсказки, стоп-краны держу для коммита и завершения. Вопрос темперамента гейта)

**«Агент может снести settings.json и все ваши гейты»** → Может, в статье это прямо сказано. Хуки - защита от забывчивости в длинной сессии, не от злонамеренного агента. Против злонамеренного нужен другой класс: права на ФС, гейты в CI вне машины агента.

**«Заголовок обещает "не может закоммитить", а обходы есть»** → Заголовок про штатный путь, обходы перечислены в границах отдельным разделом. Если после него осталось ощущение обмана - покажите, что еще вписать.

**«На днях уже была статья про хуки Claude Code (D1MANYCH)»** → Да, видел, хорошая - у него PostToolUse с exit 2 под свой проект. У меня другой контур: PreToolUse-гейт на коммит, Stop-гейт с предохранителем и эксперимент, где хук идет против прямой инструкции. Тема зрелая, решений будет много - это нормально
