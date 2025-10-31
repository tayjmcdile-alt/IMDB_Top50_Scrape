<#
setup_env.ps1
Creates a virtual environment using Python 3.9 (if available) and installs the pinned
dependencies from requirements.txt. Intended for Windows/PowerShell usage by the team.

Usage (PowerShell, run from repo root):
    .\setup_env.ps1

Notes:
- This script will try to use a Python 3.9 interpreter in common install locations. If not
  found it will fall back to the `python` command on PATH and warn if its version is not 3.9.
- The script does NOT modify repository files. It creates a per-developer `.venv` folder.
#>

Set-StrictMode -Version Latest

Write-Host "== IMDB_Top50_Scrape environment setup ==" -ForegroundColor Cyan

$candidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
    "C:\\Python39\\python.exe",
    "C:\\Program Files\\Python39\\python.exe",
    "C:\\Program Files (x86)\\Python39\\python.exe"
)

$python = $null
foreach ($p in $candidates) {
    if (Test-Path $p) {
        $python = $p
        break
    }
}

if (-not $python) {
    # fallback to whatever 'python' resolves to
    $python = (Get-Command python -ErrorAction SilentlyContinue).Source
}

if (-not $python) {
    Write-Host "ERROR: No Python executable found. Install Python 3.9 and re-run." -ForegroundColor Red
    exit 1
}

$versionOutput = & $python --version 2>&1
Write-Host "Using Python: $python ($versionOutput)"

if ($versionOutput -notmatch '3\.9') {
    Write-Warning "Recommended: use Python 3.9 for this project. The script will continue but installs may fail for C-extension packages pinned to older interpreters."
}

$venvPath = Join-Path (Get-Location) '.venv'
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at .\.venv..."
    & $python -m venv $venvPath
} else {
    Write-Host "Virtual environment .venv already exists; reusing it."
}

$venvPython = Join-Path $venvPath 'Scripts\python.exe'

Write-Host "Upgrading pip and installing requirements..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r .\requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed successfully." -ForegroundColor Green
    Write-Host "To activate the venv in PowerShell: `.`\.venv\Scripts\Activate.ps1`" -ForegroundColor Yellow
} else {
    Write-Warning "pip reported an error installing dependencies. Check the output above."
}

Write-Host "Setup finished." -ForegroundColor Cyan
