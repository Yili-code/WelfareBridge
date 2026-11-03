#!/bin/sh
# 在伺服器上執行：貼上 Cloudflare Tunnel token（輸入時不會顯示），啟動對外通道。
# token 只存在伺服器的 .tunnel.env（權限 600），不寫進程式碼、不進 git。
set -e
cd "$(dirname "$0")/.."
printf 'Cloudflare Tunnel token（貼上後按 Enter，畫面不會顯示）: '
stty -echo; read -r TOKEN; stty echo; printf '\n'
[ -n "$TOKEN" ] || { echo "沒有輸入 token"; exit 1; }
( umask 077; printf 'TUNNEL_TOKEN=%s\n' "$TOKEN" > .tunnel.env )
docker compose -f docker-compose.yml -f docker-compose.tunnel.yml up -d gate cloudflared
sleep 8
docker compose -f docker-compose.yml -f docker-compose.tunnel.yml logs --tail 8 cloudflared | sed -E 's/eyJ[A-Za-z0-9_-]+/<token>/g'
