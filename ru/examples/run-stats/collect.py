#!/usr/bin/env python3
"""Сборщик статистики сессий Claude Code.

Разбирает локальные транскрипты (~/.claude/projects/*/*.jsonl) и печатает по
каждой рабочей сессии: активные часы агента, часы присутствия человека,
счётчики инструментов, первое сообщение и дефект-кандидаты из ответов агента.

Всё выполняется локально, наружу ничего не уходит.

Запуск:
    python3 collect.py 2026-08-01     # сессии, начатые с этой даты

Метод (он же честные ограничения):
- Часы агента = «активное время»: сумма интервалов между событиями сессии,
  паузы длиннее GAP_AGENT_MIN отрезаются. Wall-clock врёт (сессии висят
  открытыми днями) - не использовать никогда.
- Часы человека = «присутствие»: то же по сообщениям пользователя, паузы
  длиннее GAP_HUMAN_MIN отрезаются. Это НИЖНЯЯ оценка - молчаливое
  наблюдение в лог не попадает.
- Сессия считается рабочей, если лежит в WORK_DIRS (папка проекта - работа
  по определению), либо - для домашней папки - сделала не меньше
  MIN_TOOL_CALLS вызовов MCP-инструментов из WORK_TOOLS.
- Транскрипты ротируются (по умолчанию 30 дней) - архивируйте сырьё, если
  датасет должен пережить ротацию.
"""
import io
import glob
import re
import json
import sys
import os
import datetime

# --- Конфиг: адаптируйте под свои проекты ------------------------------------
PROJECTS_GLOB = os.path.expanduser('~/.claude/projects/*/*.jsonl')
# Фрагменты имён папок, которые считаются работой по определению:
WORK_DIRS = ()                      # напр. ('my-e2e-repo', 'billing-service')
# Фрагменты имён папок, которые пропускаются целиком (песочницы):
SKIP_DIRS = ()                      # напр. ('sandbox', 'playground')
# Нерабочие сессии домашней папки (матч по первому сообщению):
OFF_TOPIC = re.compile(r'(?i)(блог|статья|черновик|эксперимент)')
# Семейства MCP-инструментов - маркер тестовой работы в домашней папке:
WORK_TOOLS = re.compile(r'"name":"(mcp__(?:playwright|chrome-devtools|playwright-webkit|zephyr|atlassian|figma|browserstack)__[a-zA-Z_]+)"')
# Строки в ответах агента, которые стоит прочитать как дефект-кандидаты:
DEFECT = re.compile(r'(?i)(дефект|баг(?!\w)|не работает|не отображается|расхожден|съехал|обрезан|404|500\b)')
GAP_AGENT_MIN = 30
GAP_HUMAN_MIN = 20
MIN_TOOL_CALLS = 3
# ------------------------------------------------------------------------------

TS = re.compile(r'"timestamp":"([0-9T:.\-+Z]{19,32})"')
SINCE = sys.argv[1] if len(sys.argv) > 1 else '1970-01-01'


def parse_ts(raw):
    try:
        return datetime.datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except ValueError:
        return None


def active_hours(stamps, cap_minutes):
    stamps = sorted(stamps)
    return sum(min((b - a).total_seconds(), cap_minutes * 60)
               for a, b in zip(stamps, stamps[1:])) / 3600


for path in sorted(glob.glob(PROJECTS_GLOB)):
    if any(fragment and fragment in path for fragment in SKIP_DIRS):
        continue
    stamps, user_stamps, candidates = [], [], []
    tools = {}
    first_user = None
    with io.open(path, encoding='utf-8', errors='ignore') as handle:
        for line in handle:
            match = TS.search(line)
            stamp = parse_ts(match.group(1)) if match else None
            if stamp:
                stamps.append(stamp)
            for name in WORK_TOOLS.findall(line):
                family = name.split('__')[1]
                tools[family] = tools.get(family, 0) + 1
            if '"type":"user"' in line and 'tool_use_id' not in line[:3000]:
                if stamp:
                    user_stamps.append(stamp)
                if first_user is None and '"content":"' in line:
                    start = line.find('"content":"') + 11
                    snippet = line[start:start + 220]
                    if 'system-reminder' not in snippet:
                        first_user = snippet.replace('\\n', ' ')[:150]
            if '"type":"assistant"' in line and DEFECT.search(line):
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                for chunk in ((record.get('message') or {}).get('content') or []):
                    if isinstance(chunk, dict) and chunk.get('type') == 'text':
                        for hit in DEFECT.finditer(chunk.get('text', '')):
                            text = chunk['text']
                            snippet = text[max(0, hit.start() - 50):hit.start() + 100]
                            snippet = snippet.replace('\n', ' ').strip()
                            if len(candidates) < 8 and all(snippet[:30] not in c for c in candidates):
                                candidates.append(snippet)
    if not stamps:
        continue
    if min(stamps).strftime('%Y-%m-%d') < SINCE:
        continue
    is_work_dir = any(fragment and fragment in path for fragment in WORK_DIRS)
    if not is_work_dir and sum(tools.values()) < MIN_TOOL_CALLS:
        continue
    if not is_work_dir and first_user and OFF_TOPIC.search(first_user):
        continue
    agent_h = active_hours(stamps, GAP_AGENT_MIN)
    human_h = active_hours(user_stamps, GAP_HUMAN_MIN) if len(user_stamps) >= 2 else 0.0
    top_tools = dict(sorted(tools.items(), key=lambda kv: -kv[1])[:3])
    session_id = path.split('/')[-1][:8]
    day = min(stamps).strftime('%Y-%m-%d')
    print(f"\n===== {session_id} | {day} | агент ~{agent_h:.1f}ч | человек ~{human_h:.1f}ч | инструменты: {top_tools}")
    print(f"  первое сообщение: {first_user}")
    for candidate in candidates:
        print(f"  кандидат: {candidate[:140]}")
