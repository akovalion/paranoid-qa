#!/bin/bash
# PreToolUse gate: git commit is allowed only with a fresh green test run.
# Input: JSON on stdin. Block: exit 0 + permissionDecision=deny.

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Only act on git commit, leave the rest of Bash alone
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

[ -f "$RUN_FILE" ] || deny "Commit blocked: no test-run artifact ($RUN_FILE). Run first: npx playwright test"

STATUS=$(jq -r '.status // "unknown"' "$RUN_FILE")
[ "$STATUS" = "passed" ] || deny "Commit blocked: last run is not green (status: $STATUS). Fix the tests and re-run"

STALE=$(find tests -name '*.ts' -newer "$RUN_FILE" 2>/dev/null | head -5)
[ -z "$STALE" ] || deny "Commit blocked: tests changed after the last run ($(echo "$STALE" | tr '\n' ' ')). Run: npx playwright test"

# State cross-check: dirty flag not older than the run -> deny when in doubt
FLAG=".claude/state/tests-dirty"
if [ -f "$FLAG" ] && ! [ "$FLAG" -ot "$RUN_FILE" ]; then
  deny "Commit blocked: a test edit was recorded after the last run (tests-dirty flag). Run: npx playwright test"
fi

exit 0
