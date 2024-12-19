@echo off
title Gerenciador de Disco Avancado
echo.
echo =====================================
echo    GERENCIADOR DE DISCO AVANCADO
echo =====================================
echo.
echo Iniciando com privilegios de administrador...
echo.

:: Verifica se ja esta rodando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run
) else (
    goto :elevate
)

:elevate
:: Solicita privilegios de administrador
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && python gerenciador_disco_admin.py && pause' -Verb RunAs"
exit

:run
python gerenciador_disco_admin.py
pause
