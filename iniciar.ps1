param([switch]$ConEjemplos, [int]$Puerto = 8011)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonPanorama = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPanorama)) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno. Instala Python 3.10 o superior.' }
}
& $pythonPanorama -m pip install -r requirements-local.txt
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias.' }
& $pythonPanorama backend/manage.py migrate --settings=config.settings_local --noinput
if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar la base local.' }
if ($ConEjemplos) {
    & $pythonPanorama backend/manage.py seed_design --settings=config.settings_local
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron cargar los ejemplos.' }
}
Write-Host "Panorama: http://127.0.0.1:$Puerto"
Write-Host 'Ctrl+C detiene el servidor. No se crean cuentas por defecto.'
& $pythonPanorama backend/manage.py runserver "127.0.0.1:$Puerto" --settings=config.settings_local --noreload
