#!/usr/bin/env bash
# Replays the real testing-skill run for the demo GIF (time-compressed).
# The report text is a condensed excerpt of an actual, unedited session output.
DIR="$(cd "$(dirname "$0")" && pwd)"
CMD='claude "Use the testing skill to test the feedback form at http://localhost:8787 - check the submit flow and inspect the actual POST payload."'

printf '\e[2J\e[H'
sleep 0.7
printf '\e[2m$\e[0m '
for ((i = 0; i < ${#CMD}; i++)); do
  printf '%s' "${CMD:i:1}"
  sleep 0.018
done
sleep 0.8
printf '\n\n'

steps=(
  "⏺ Reading skill references: frontend.md, cross-cutting.md…"
  "⏺ Driving the form in Chromium: fill → submit → toast…"
  "⏺ Capturing network: POST /api/feedback × 3…"
)
for s in "${steps[@]}"; do
  printf '\e[2m%s\e[0m\n' "$s"
  sleep 1.5
done
sleep 0.8
printf '\n'

while IFS= read -r line; do
  printf '%b\n' "$line"
  sleep 0.07
done < "$DIR/report.txt"
sleep 6
