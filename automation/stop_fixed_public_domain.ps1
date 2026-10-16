$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$pidPath = Join-Path $projectRoot '.codex-automation\cloudflared-fixed\cloudflared-fixed.pid'
$runtimeConfigPath = Join-Path $projectRoot 'common\runtime-config.js'

if (Test-Path $pidPath) {
  $processId = Get-Content $pidPath -ErrorAction SilentlyContinue
  if ($processId) {
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) {
      Stop-Process -Id $processId -Force
      Write-Output "Stopped fixed-domain cloudflared process $processId"
    }
  }
  Remove-Item $pidPath -Force
}

Set-Content -Path $runtimeConfigPath -Value "export const RUNTIME_API_BASE_URL = ''`r`n" -Encoding utf8
Write-Output "Cleared runtime API override."
