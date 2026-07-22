#!/bin/bash
# Stop-гейт: нельзя завершить ход, если тесты менялись, а прогона после правки не было.
# Самоочистка: свежий прогон снимает флаг. Предохранитель: не блокируем больше 2 раз подряд.

FLAG=".claude/state/tests-dirty"
RUN_FILE="test-results/.last-run.json"

[ -f "$FLAG" ] || exit 0

# Прогон не старше правки - флаг снимается, стоп разрешён.
# Сравнение "флаг НЕ новее прогона": при равных секундах пропускаем (анти-цикл),
# строгий контроль свежести остаётся на gate-commit.
if [ -f "$RUN_FILE" ] && ! [ "$FLAG" -nt "$RUN_FILE" ]; then
  rm -f "$FLAG"
  exit 0
fi

# Предохранитель от бесконечного цикла
ATTEMPTS=$(cat "$FLAG" 2>/dev/null || echo 0)
if [ "$ATTEMPTS" -ge 2 ]; then
  rm -f "$FLAG"
  jq -n '{systemMessage: "gate-stop: лимит блокировок исчерпан, пропускаю. Тесты так и не прогнаны!"}'
  exit 0
fi
echo $((ATTEMPTS + 1)) > "$FLAG"

jq -n '{
  decision: "block",
  reason: "Тесты менялись, но прогона после правки не было. Запусти npx playwright test и убедись, что зелёно, прежде чем завершать"
}'
exit 0
