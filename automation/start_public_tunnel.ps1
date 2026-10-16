$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$cloudflaredPath = 'C:\Users\admin\AppData\Local\Microsoft\WinGet\Links\cloudflared.exe'
$localBackendUrl = 'http://127.0.0.1:5000'
$stateDir = Join-Path $projectRoot '.codex-automation\cloudflared'
$logPath = Join-Path $stateDir 'cloudflared.log'
$pidPath = Join-Path $stateDir 'cloudflared.pid'
$runtimeConfigPath = Join-Path $projectRoot 'common\runtime-config.js'

New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

if (-not (Test-Path $cloudflaredPath)) {
  throw "cloudflared.exe not found at $cloudflaredPath"
}

try {
  $health = Invoke-WebRequest -UseBasicParsing "$localBackendUrl/api/health" -TimeoutSec 5
  if ($health.StatusCode -lt 200 -or $health.StatusCode -ge 300) {
    throw "Backend health check returned HTTP $($health.StatusCode)"
  }
} catch {
  throw "Local backend is not reachable at $localBackendUrl. Start python_backend/server.py first."
}

if (Test-Path $pidPath) {
  $oldPid = Get-Content $pidPath -ErrorAction SilentlyContinue
  if ($oldPid) {
    $process = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
    if ($process) {
      Stop-Process -Id $oldPid -Force
      Start-Sleep -Seconds 1
    }
  }
}

if (Test-Path $logPath) {
  Remove-Item $logPath -Force
}

$process = Start-Process -FilePath $cloudflaredPath -ArgumentList @('tunnel', '--url', $localBackendUrl, '--logfile', $logPath) -PassThru -WindowStyle Hidden
$process.Id | Set-Content -Path $pidPath -Encoding ascii

$publicUrl = $null
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Seconds 1
  if (Test-Path $logPath) {
    $match = Select-String -Path $logPath -Pattern 'https://[-a-z0-9]+\.trycloudflare\.com' -AllMatches -ErrorAction SilentlyContinue | Select-Object -Last 1
    if ($match -and $match.Matches.Count -gt 0) {
      $publicUrl = $match.Matches[$match.Matches.Count - 1].Value
      break
    }
  }
  if ($process.HasExited) {
    throw "cloudflared exited early. Check $logPath"
  }
}

if (-not $publicUrl) {
  throw "Timed out waiting for the public tunnel URL. Check $logPath"
}

$runtimeContent = @(
  "export const RUNTIME_API_BASE_URL = '$publicUrl'"
  ''
) -join [Environment]::NewLine

Set-Content -Path $runtimeConfigPath -Value $runtimeContent -Encoding utf8

Write-Output "Public tunnel ready:"
Write-Output $publicUrl
Write-Output ""
Write-Output "Updated:"
Write-Output $runtimeConfigPath
Write-Output ""
Write-Output "Rebuild the mini program after changing the runtime config."
