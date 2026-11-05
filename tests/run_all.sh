#!/usr/bin/env bash
# Барча тестларни кетма-кет ишга туширади.
# Ишлатиш:  bash tests/run_all.sh          — ҳаммаси
#           bash tests/run_all.sh t_50     — номида t_50 бор тестлар
cd "$(dirname "$0")"
F="${1:-}"
PASS=0; FAIL=0; FAILED=""
for t in $(ls t_*.py | sort); do
  case "$t" in *"$F"*) ;; *) continue ;; esac
  printf '\n\033[1m── %s\033[0m\n' "$t"
  if timeout 300 python3 "$t"; then PASS=$((PASS+1));
  else FAIL=$((FAIL+1)); FAILED="$FAILED $t"; fi
done
printf '\n\033[1m═══ Натижа: %d ўтди, %d йиқилди\033[0m\n' "$PASS" "$FAIL"
[ -n "$FAILED" ] && printf 'Йиқилганлар:%s\n' "$FAILED"
[ "$FAIL" -eq 0 ]
