$ErrorActionPreference = 'Stop'
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Host 'Edit .env and set DJANGO_SECRET_KEY and SETUP_SECRET before continuing.' -ForegroundColor Yellow
