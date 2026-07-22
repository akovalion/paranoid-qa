#!/bin/bash
# PreToolUse-гейт: git commit разрешён только при свежем зелёном прогоне тестов.
# Вход: JSON на stdin. Блок: exit 0 + permissionDecision=deny.

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Работаем только с git commit, остальной Bash не трогаем
echo "$CMD" | grep -qE '(^|[;&|]\s*)git\s+commit' || exit 0

deny() {
  jq -n --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
}

RUN_FILE="test-results/.last-run.json"

[ -f "$RUN_FILE" ] || deny "Коммит заблокирован: нет артефакта прогона ($RUN_FILE). Сначала запусти: npx playwright test"

STATUS=$(jq -r '.status // "unknown"' "$RUN_FILE")
[ "$STATUS" = "passed" ] || deny "Коммит заблокирован: последний прогон не зелёный (status: $STATUS). Почини тесты и прогони заново"

STALE=$(find tests -name '*.ts' -newer "$RUN_FILE" 2>/dev/null | head -5)
[ -z "$STALE" ] || deny "Коммит заблокирован: тесты менялись после последнего прогона ($(echo "$STALE" | tr '\n' ' ')). Прогони: npx playwright test"

# Дублирующий стейт-чек: флаг "грязных тестов" не старше прогона -> в сомнении запрещаем
FLAG=".claude/state/tests-dirty"
if [ -f "$FLAG" ] && ! [ "$FLAG" -ot "$RUN_FILE" ]; then
  deny "Коммит заблокирован: правка тестов зафиксирована после прогона (флаг tests-dirty). Прогони: npx playwright test"
fi

exit 0
