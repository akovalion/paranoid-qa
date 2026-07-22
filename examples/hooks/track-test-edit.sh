#!/bin/bash
# PostToolUse: editing a spec raises the "tests dirty" flag and reminds the agent to run them.

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

echo "$FILE" | grep -qE '\.spec\.ts$' || exit 0

mkdir -p .claude/state
echo 0 > .claude/state/tests-dirty

jq -n '{
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: "A test file was modified. A test run is mandatory before committing and before finishing: npx playwright test"
  }
}'
exit 0
