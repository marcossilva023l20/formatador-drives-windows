@echo off
echo Iniciando Gerenciador de Disco com privilegios de administrador...
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/k cd /d %~dp0 && python gerenciador_disco_admin.py && pause'"
