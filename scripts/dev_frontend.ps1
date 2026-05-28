$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot/../src/frontend"
if (-Not (Test-Path "node_modules")) {
  npm install
}
npm run dev
