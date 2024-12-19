# Inicia o programa com privilégios de administrador
$pythonPath = (Get-Command python).Source
$scriptPath = Join-Path $PSScriptRoot "gerenciador_disco_admin.py"

Write-Host "Iniciando Gerenciador de Disco como Administrador..."
Start-Process -FilePath $pythonPath -ArgumentList $scriptPath -Verb RunAs -Wait
