# Bootstrap a new meta repo from kbhatiya999/harbor.
# Usage: irm https://raw.githubusercontent.com/kbhatiya999/harbor/main/setup.ps1 | iex
#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

$Repo  = "kbhatiya999/harbor"
$PyPkg = "harbor-meta"
$GoMod = "github.com/$Repo"

# ── prefer uvx (Python, no install step) ─────────────────────────────────────

if (Get-Command uvx -ErrorAction SilentlyContinue) {
    & uvx --from $PyPkg harbor @args
    exit $LASTEXITCODE
}

# ── then npx (Node, no install step) ─────────────────────────────────────────

if (Get-Command npx -ErrorAction SilentlyContinue) {
    & npx --yes "@kbhatiya999/harbor" @args
    exit $LASTEXITCODE
}

# ── then go run (Go, no install step) ──────────────────────────────────────

if (Get-Command go -ErrorAction SilentlyContinue) {
    & go run "${GoMod}@latest" @args
    exit $LASTEXITCODE
}

# ── detect architecture ───────────────────────────────────────────────────────

$Arch = if ([System.Environment]::Is64BitOperatingSystem) { "amd64" } else { "386" }

# ARM64 detection (Windows 11 on ARM)
if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { $Arch = "arm64" }

# ── resolve latest release tag ────────────────────────────────────────────────

$Release = Invoke-RestMethod "https://api.github.com/repos/$Repo/releases/latest"
$Tag     = $Release.tag_name

if (-not $Tag) {
    Write-Error "Could not resolve latest release from $Repo."
    exit 1
}

# ── download binary ───────────────────────────────────────────────────────────

$Bin  = "harbor-windows-${Arch}.exe"
$Url  = "https://github.com/$Repo/releases/download/$Tag/$Bin"
$Tmp  = Join-Path $env:TEMP $Bin

Write-Host "Downloading harbor $Tag (windows/$Arch)..." -ForegroundColor Cyan
Invoke-WebRequest $Url -OutFile $Tmp

# ── run ───────────────────────────────────────────────────────────────────────

& $Tmp @args
