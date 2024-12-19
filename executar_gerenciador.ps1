# Requer privilégios de administrador
#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

try {
    # Obtém o diretório atual do script
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    
    # Muda para o diretório do script
    Set-Location -Path $scriptPath
    
    Write-Host "`nIniciando Gerenciador de Disco...`n"
    
    # Executa o script Python
    & python gerenciador_disco_admin.py
}
catch {
    Write-Host "`nErro ao executar o programa: $_`n" -ForegroundColor Red
}
finally {
    Write-Host "`nPressione qualquer tecla para sair..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
