@echo off
powershell -Command "Start-Process cmd -ArgumentList '/k cd /d %~dp0 && python gerenciador_disco_admin.py && pause' -Verb RunAs"
