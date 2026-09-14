$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$nodePath = (Get-Command node).Source
$npmCli = Join-Path (Split-Path $nodePath) 'node_modules\npm\bin\npm-cli.js'
if (-not (Test-Path -LiteralPath $npmCli)) { throw '請安裝包含 npm 的 Node.js 24。' }
& $nodePath $npmCli ci --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw 'Node dependencies failed' }
if (-not (Test-Path 'backend/.venv/Scripts/python.exe')) {
    if ($env:PYTHON) { & $env:PYTHON -m venv backend/.venv } else { py -3 -m venv backend/.venv }
    if ($LASTEXITCODE -ne 0) { throw '需要 Python 3.12 或更新版本，也可設定 PYTHON 為執行檔路徑。' }
}
& ./backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependencies failed' }
if (-not (Get-ChildItem data/tools/mongodb -Filter mongod.exe -Recurse -ErrorAction SilentlyContinue)) {
    & ./backend/.venv/Scripts/python.exe scripts/install_mongo.py
    if ($LASTEXITCODE -ne 0) { throw 'MongoDB download failed' }
}
Write-Output '安裝完成。執行 Start-WelfareBridge.cmd 啟動。'
