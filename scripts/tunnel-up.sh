#!/bin/sh
# 在伺服器上執行：貼上 Cloudflare Tunnel token（輸入時不會顯示），啟動對外通道。
# token 只存在伺服器的 .tunnel.env（權限 600），不寫進程式碼、不進 git。
set -e
cd "$(dirname "$0")/.."
printf 'Cloudflare Tunnel token（貼上後按 Enter，畫面不會顯示）: '
stty -echo; read -r TOKEN; stty echo; printf '\n'
# 整行指令或貼了兩次也沒關係：只取第一段 eyJ 開頭的 token
TOKEN=$(printf '%s' "$TOKEN" | tr -d '[:space:]' | sed 's/^.*install//' | awk '{ i = index(substr($0, 2), "eyJhIjoi"); print (i > 0) ? substr($0, 1, i) : $0 }')
case "$TOKEN" in eyJ*) ;; *) echo "這不是 Tunnel token（應該以 eyJ 開頭），請重新複製"; exit 1;; esac
echo "收到 token，長度 ${#TOKEN}"
( umask 077; printf 'TUNNEL_TOKEN=%s\n' "$TOKEN" > .tunnel.env )
docker compose -f docker-compose.yml -f docker-compose.tunnel.yml up -d gate cloudflared
sleep 8
docker compose -f docker-compose.yml -f docker-compose.tunnel.yml logs --tail 8 cloudflared | sed -E 's/eyJ[A-Za-z0-9_-]+/<token>/g'
