#!/bin/bash
clear
echo -e "\033[0m"  # Reset cor
python3 formatar_drive_cmd.py

# Se o Python3 não estiver disponível, tenta com python
if [ $? -ne 0 ]; then
    python formatar_drive_cmd.py
fi

read -p "Pressione ENTER para sair..."
