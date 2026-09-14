@echo off
chcp 65001 >nul
cd /d "%~dp0"
docker info >nul 2>&1
if errorlevel 1 (
  echo 找不到執行中的 Docker。請先開啟 Docker Desktop，等左下角顯示 Engine running 後再執行一次。
  pause
  exit /b 1
)
if not exist ".env.local" copy ".env.local.example" ".env.local" >nul
echo 建置並啟動 WelfareBridge（第一次需要下載映像，會比較久）...
docker compose up -d --build --wait
if errorlevel 1 (
  echo 啟動失敗，請查看 Docker Desktop 的 Containers 頁面，或執行 docker compose logs
  pause
  exit /b 1
)
start "" http://localhost:3000
echo 已啟動：http://localhost:3000 。停止請執行 docker compose down，或在 Docker Desktop 按停止。
timeout /t 5 >nul
