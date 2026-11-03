#!/bin/sh
# 在伺服器上執行：設定後台密碼（輸入時不會顯示），寫入 .env.local 後重建網頁容器（約 10 秒中斷）。
set -e
cd "$(dirname "$0")/.."
printf '新的後台密碼（至少 10 字元，輸入時不會顯示）: '
stty -echo; read -r PASS; stty echo; printf '\n'
printf '再輸入一次: '
stty -echo; read -r PASS2; stty echo; printf '\n'
[ "$PASS" = "$PASS2" ] || { echo "兩次輸入不一致"; exit 1; }
[ "${#PASS}" -ge 10 ] || { echo "太短了，請至少 10 個字元"; exit 1; }
case "$PASS" in *[\"\'\\$\`\ ]*) echo "請不要包含空白、引號、\ 或 \$"; exit 1;; esac
touch .env.local; chmod 600 .env.local
grep -v '^WELFARE_ADMIN_PASSWORD=' .env.local > .env.local.new || true
printf 'WELFARE_ADMIN_PASSWORD=%s\n' "$PASS" >> .env.local.new
mv .env.local.new .env.local; chmod 600 .env.local
docker compose up -d --force-recreate --no-deps web
echo "完成，後台密碼已更新（長度 ${#PASS}）"
