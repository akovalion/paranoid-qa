#!/bin/bash
# PostToolUse: правка спеки поднимает флаг "тесты грязные" и напоминает агенту про прогон.

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

echo "$FILE" | grep -qE '\.spec\.ts$' || exit 0

mkdir -p .claude/state
echo 0 > .claude/state/tests-dirty

jq -n '{
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: "Тестовый файл изменён. До коммита и до завершения работы обязателен прогон: npx playwright test"
  }
}'
exit 0
