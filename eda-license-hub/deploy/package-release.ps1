$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $root 'release'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$tarPath = Join-Path $outDir 'license-portal-release.tar.gz'
if (Test-Path $tarPath) { Remove-Item $tarPath -Force }

# Exclude heavy/generated dirs
$tmp = Join-Path $env:TEMP ("license-portal-release-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

Copy-Item -Recurse -Force (Join-Path $root '*') $tmp

$remove = @(
  'frontend/node_modules',
  'frontend/dist',
  'backend/.venv',
  'backend/__pycache__',
  '.git',
  'release'
)

foreach ($r in $remove) {
  $p = Join-Path $tmp $r
  if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}

Push-Location $tmp
tar -czf $tarPath .
Pop-Location

Remove-Item -Recurse -Force $tmp
Write-Host "Release package created: $tarPath"
