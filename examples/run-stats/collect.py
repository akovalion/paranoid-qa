#!/usr/bin/env python3
"""Claude Code session stats collector.

Parses your local Claude Code transcripts (~/.claude/projects/*/*.jsonl) and
prints, per work session: active agent hours, human presence hours, tool-call
counts, the opening message, and defect-candidate lines from agent replies.

Everything runs locally; nothing leaves your machine.

Usage:
    python3 collect.py 2026-08-01     # sessions started on/after this date

Method (also the honest limitations):
- Agent hours = "active time": sum of gaps between consecutive session events,
  gaps longer than GAP_AGENT_MIN are cut. Wall-clock lies (sessions stay open
  for days) - never use it.
- Human hours = "presence": same over the user's own messages, gaps longer
  than GAP_HUMAN_MIN are cut. This is a LOWER bound - silent watching is
  invisible to the log.
- A session counts as work if it lives in one of WORK_DIRS (project folders
  are work by definition), or - for the home folder - if it made at least
  MIN_TOOL_CALLS calls to the MCP tools listed in WORK_TOOLS.
- Transcripts rotate (30 days by default) - archive raw files if you want
  your dataset to outlive the rotation.
"""
import io
import glob
import re
import json
import sys
import os
import datetime

# --- Config: adapt these to your projects -----------------------------------
PROJECTS_GLOB = os.path.expanduser('~/.claude/projects/*/*.jsonl')
# Folder-name fragments that are work by definition (your repos/projects):
WORK_DIRS = ()                      # e.g. ('my-e2e-repo', 'billing-service')
# Folder-name fragments to skip entirely (sandboxes, experiments):
SKIP_DIRS = ()                      # e.g. ('sandbox', 'playground')
# Off-topic sessions in the home folder (matched against the first message):
OFF_TOPIC = re.compile(r'(?i)(blog|article|draft|experiment)')
# MCP tool families that mark a home-folder session as testing work:
WORK_TOOLS = re.compile(r'"name":"(mcp__(?:playwright|chrome-devtools|playwright-webkit|zephyr|atlassian|figma|browserstack)__[a-zA-Z_]+)"')
# Lines in agent replies worth reading as defect candidates:
DEFECT = re.compile(r'(?i)(defect|bug(?!\w)|broken|does not work|mismatch|404|500\b|дефект|баг(?!\w)|не работает|расхожден)')
GAP_AGENT_MIN = 30
GAP_HUMAN_MIN = 20
MIN_TOOL_CALLS = 3
# -----------------------------------------------------------------------------

TS = re.compile(r'"timestamp":"([0-9T:.\-+Z]{19,32})"')
SINCE = sys.argv[1] if len(sys.argv) > 1 else '1970-01-01'
print("NOTE: candidates are unconfirmed hints - count only session-FINAL verdicts, not mid-session totals.")


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
    print(f"\n===== {session_id} | {day} | agent ~{agent_h:.1f}h | human ~{human_h:.1f}h | tools: {top_tools}")
    print(f"  first message: {first_user}")
    for candidate in candidates:
        print(f"  candidate: {candidate[:140]}")
