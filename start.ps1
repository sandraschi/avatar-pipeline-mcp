# Start avatar-pipeline-mcp backend + webapp
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root'; uv run avatar-pipeline-mcp"
Start-Sleep -Seconds 2
Set-Location "$Root\webapp"
if (-not (Test-Path node_modules)) { npm install }
npm run dev
