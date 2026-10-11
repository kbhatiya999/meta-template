# Run harbor without installing it.
# Usage: irm https://raw.githubusercontent.com/kbhatiya999/meta-template/main/setup.ps1 | iex
#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
    Write-Host "harbor runs on uv. Install it first:"
    Write-Host '  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
    exit 1
}

& uvx harbor-meta @args
exit $LASTEXITCODE
