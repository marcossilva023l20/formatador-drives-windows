@echo off
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c cd /d %~dp0 && python gerenciador_disco.py'"
