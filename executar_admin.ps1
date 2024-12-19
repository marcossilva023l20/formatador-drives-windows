# Solicita privilégios de administrador
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
    $arguments = "& '" + $myinvocation.mycommand.definition + "'"
    Start-Process powershell -Verb runAs -ArgumentList $arguments
    Break
}

# Muda para o diretório do script
Set-Location $PSScriptRoot

# Executa o gerenciador de disco
python gerenciador_disco_admin.py

# Aguarda input do usuário antes de fechar
Write-Host "`nPressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
