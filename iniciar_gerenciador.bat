@echo off
echo Iniciando Gerenciador de Disco como Administrador...
powershell -Command "Start-Process -FilePath 'python.exe' -ArgumentList '%~dp0gerenciador_disco_admin.py' -Verb RunAs -Wait"