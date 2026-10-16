$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$cloudflaredPath = 'C:\Users\admin\AppData\Local\Microsoft\WinGet\Links\cloudflared.exe'
$localBackendUrl = 'http://127.0.0.1:5000'
$publicUrl = 'https://api.aurapose.tech'
$tunnelId = '0789603e-7238-4ca8-867b-9c4e4bf85b37'
$credentialsPath = "C:\Users\admin\.cloudflared\$tunnelId.json"
$stateDir = Join-Path $projectRoot '.codex-automation\cloudflared-fixed'
$configPath = Join-Path $stateDir 'config.yml'
$stdoutLogPath = Join-Path $stateDir 'cloudflared-fixed.out.log'
$stderrLogPath = Join-Path $stateDir 'cloudflared-fixed.err.log'
$pidPath = Join-Path $stateDir 'cloudflared-fixed.pid'
$runtimeConfigPath = Join-Path $projectRoot 'common\runtime-config.js'

New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

if (-not (Test-Path $cloudflaredPath)) {
  throw "cloudflared.exe not found at $cloudflaredPath"
}

if (-not (Test-Path $credentialsPath)) {
  throw "Tunnel credentials not found at $credentialsPath"
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

if (Test-Path $stdoutLogPath) {
  Remove-Item $stdoutLogPath -Force
}

if (Test-Path $stderrLogPath) {
  Remove-Item $stderrLogPath -Force
}

$configLines = @(
  "tunnel: $tunnelId"
  "credentials-file: $credentialsPath"
  "ingress:"
  "  - hostname: api.aurapose.tech"
  "    service: $localBackendUrl"
  "  - service: http_status:404"
)
Set-Content -Path $configPath -Value ($configLines -join [Environment]::NewLine) -Encoding ascii

$process = Start-Process -FilePath $cloudflaredPath -ArgumentList @('tunnel', '--config', $configPath, 'run') -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutLogPath -RedirectStandardError $stderrLogPath
$process.Id | Set-Content -Path $pidPath -Encoding ascii

$ready = $false
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Seconds 1
  if ($process.HasExited) {
    throw "cloudflared exited early. Check $stdoutLogPath and $stderrLogPath"
  }
  try {
    $remoteHealth = Invoke-WebRequest -UseBasicParsing "$publicUrl/api/health" -TimeoutSec 5
    if ($remoteHealth.StatusCode -ge 200 -and $remoteHealth.StatusCode -lt 300) {
      $ready = $true
      break
    }
  } catch {
    # DNS/edge propagation may take a moment.
  }
}

if (-not $ready) {
  throw "Timed out waiting for $publicUrl to become reachable. Check $stdoutLogPath and $stderrLogPath"
}

$runtimeContent = @(
  "export const RUNTIME_API_BASE_URL = '$publicUrl'"
  ''
) -join [Environment]::NewLine

Set-Content -Path $runtimeConfigPath -Value $runtimeContent -Encoding utf8

Write-Output "Fixed public domain ready:"
Write-Output $publicUrl
Write-Output ""
Write-Output "Tunnel ID:"
Write-Output $tunnelId
Write-Output ""
Write-Output "Updated:"
Write-Output $runtimeConfigPath
Write-Output ""
Write-Output "Rebuild the mini program after changing the runtime config."
