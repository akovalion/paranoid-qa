#!/bin/bash
# Stop gate: the agent cannot finish the turn if tests were edited and never run afterwards.
# Self-clearing: a fresh run removes the flag. Fuse: never block more than 2 times in a row.

FLAG=".claude/state/tests-dirty"
RUN_FILE="test-results/.last-run.json"

[ -f "$FLAG" ] || exit 0

# The run is not older than the edit - clear the flag, allow the stop.
# "flag NOT newer than run": on equal timestamps we let through (anti-loop);
# strict freshness stays on gate-commit.
if [ -f "$RUN_FILE" ] && ! [ "$FLAG" -nt "$RUN_FILE" ]; then
  rm -f "$FLAG"
  exit 0
fi

# Fuse against infinite block loops
ATTEMPTS=$(cat "$FLAG" 2>/dev/null || echo 0)
if [ "$ATTEMPTS" -ge 2 ]; then
  rm -f "$FLAG"
  jq -n '{systemMessage: "gate-stop: block limit reached, letting through. Tests were never run!"}'
  exit 0
fi
echo $((ATTEMPTS + 1)) > "$FLAG"

jq -n '{
  decision: "block",
  reason: "Tests were modified but never run afterwards. Run npx playwright test and make sure it is green before finishing"
}'
exit 0
