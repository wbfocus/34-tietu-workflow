#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Scripts = Join-Path $RepoRoot ".cursor\skills\34-tietu-workflow\scripts"
$Browsers = Join-Path $RepoRoot ".playwright-browsers"

Write-Host "Repo: $RepoRoot"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "未找到 node。请先安装 Node.js 20+"
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  throw "未找到 npm"
}
$py = $null
foreach ($c in @("py", "python")) {
  if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}
if (-not $py) { throw "未找到 Python。请安装 Python 3，并确保 py 或 python 在 PATH" }
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Warning "未找到 ffmpeg。合成 MP4 需要 ffmpeg，请安装后重新打开终端。"
}

New-Item -ItemType Directory -Force -Path $Browsers | Out-Null
$env:PLAYWRIGHT_BROWSERS_PATH = $Browsers
if (Test-Path "D:\devtools\npm-cache") {
  $env:npm_config_cache = "D:\devtools\npm-cache"
}

Set-Location $Scripts
npm install
npx playwright install chromium
Write-Host "OK  Playwright Chromium -> $Browsers"
Write-Host "下次出图前若换电脑，再跑一次本脚本即可。"
