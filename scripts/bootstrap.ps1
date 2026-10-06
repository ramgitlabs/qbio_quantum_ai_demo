$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    & py -3.12 -m venv .venv
} else {
    $fallback = Get-Command python -ErrorAction SilentlyContinue
    if (-not $fallback) {
        throw 'Python 3.12 or newer is required. Install Python 3.12 and re-run this script.'
    }
    & python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m pip install -e .

Write-Host "Environment ready. Run:"
Write-Host "  .\.venv\Scripts\python.exe -m qbio_diagnostics.run_demo --samples 160 --qubits 4"
