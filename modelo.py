import os
import subprocess
import string
import re
from ctypes import windll

def validar_opcao(opcao, opcoes_validas):
    """Valida se a opção é única e está nas opções válidas"""
    # Remove espaços no início e fim
    opcao = opcao.strip()
    # Verifica se contém espaços no meio
    if ' ' in opcao:
        return None
    # Verifica se tem apenas um caractere
    if len(opcao) != 1:
        return None
    # Verifica se está nas opções válidas
    return opcao if opcao in opcoes_validas else None

def limpar_nome_volume(nome):
    """Limpa e formata o nome do volume"""
    if not nome:
        return None
    # Remove aspas e espaços extras
    nome = nome.strip('" ').strip()
    # Substitui espaços por underscores
    nome = nome.replace(' ', '_')
    # Remove caracteres especiais
    nome = re.sub(r'[^a-zA-Z0-9_-]', '', nome)
    # Limita a 11 caracteres
    nome = nome[:11]
    return nome

def obter_tamanho_drive(letra):
    """Retorna o tamanho do drive em GB"""
    try:
        resultado = subprocess.check_output(
            f'wmic logicaldisk where "DeviceID=\'{letra}:\'" get size /value',
            shell=True
        ).decode()
        tamanho = int(resultado.split('=')[1].strip()) / (1024**3)  # Converte para GB
        return tamanho
    except:
        return 0

def obter_nome_volume(letra):
    """Retorna o nome do volume do drive"""
    try:
        resultado = subprocess.check_output(
            f'wmic logicaldisk where "DeviceID=\'{letra}:\'" get volumename',
            shell=True
        ).decode()
        return resultado.split('\n')[1].strip()
    except:
        return ""

def obter_drives():
    """Retorna lista de drives disponíveis"""
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letra in string.ascii_uppercase:
        if bitmask & 1:
            try:
                subprocess.check_output(f'wmic logicaldisk where "DeviceID=\'{letra}:\'" get DeviceID,VolumeName')
                drives.append(letra)
            except:
                pass
        bitmask >>= 1
    return drives

def mostrar_drives():
    """Mostra informações detalhadas dos drives"""
    print("\nDrives disponíveis:")
    print("-" * 70)
    print("Letra  | Nome do Volume                    | Tamanho")
    print("-" * 70)
    
    for drive in obter_drives():
        try:
            tamanho = obter_tamanho_drive(drive)
            volume = obter_nome_volume(drive)
            print(f"{drive}:     | {volume:<30} | {tamanho:.1f} GB")
        except:
            continue
    print("-" * 70)

def formatar_drive(letra_drive, sistema_arquivos, nome_volume=None):
    """Formata o drive especificado"""
    print(f"\nFormatando drive {letra_drive}: para {sistema_arquivos}...")
    print("Isso pode levar alguns minutos...\n")
    
    # Monta o comando de formatação
    comando = f'format {letra_drive}: /FS:{sistema_arquivos} /Q'
    if nome_volume:
        nome_volume = limpar_nome_volume(nome_volume)
        if nome_volume:
            comando += f' /V:{nome_volume}'
    comando += ' /Y'
    
    print(f"Executando comando: {comando}\n")
    
    try:
        subprocess.run(comando, shell=True, check=True)
        print("\nFormatação concluída com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nErro durante a formatação: {str(e)}")
        return False

def main():
    print("\n" + "=" * 50)
    print("        FORMATADOR DE DRIVES")
    print("=" * 50)
    print("\nATENÇÃO: Use este programa com cuidado!")
    
    # Lista drives disponíveis
    mostrar_drives()
    
    # Solicita drive para formatar
    while True:
        drive = input("\nDigite a letra do drive para formatar (ex: F) ou X para sair: ").upper()
        if drive == 'X':
            print("\nPrograma finalizado.")
            return
        if drive and drive in obter_drives():
            break
        print("Drive inválido! Tente novamente.")
    
    # Obtém tamanho e nome atual do drive
    tamanho = obter_tamanho_drive(drive)
    nome_atual = limpar_nome_volume(obter_nome_volume(drive))
    
    # Menu de sistema de arquivos
    print("\nEscolha o sistema de arquivos:")
    print("-" * 30)
    if tamanho > 32:
        print("[1] FAT32 (Não recomendado - Drive maior que 32GB)")
    else:
        print("[1] FAT32")
    print("[2] exFAT (Recomendado para drives externos)")
    print("[3] NTFS  (Recomendado para drives internos)")
    print("[X] Cancelar")
    print("-" * 30)
    
    if tamanho > 32:
        print("\nNOTA: Este drive tem {:.1f} GB. O Windows pode ter".format(tamanho))
        print("problemas para formatar em FAT32 drives maiores que 32GB.")
        print("Recomendamos usar exFAT ou NTFS.")
    
    while True:
        opcao = input("\nDigite sua escolha (1, 2, 3 ou X): ").upper()
        opcao = validar_opcao(opcao, ['1', '2', '3', 'X'])
        if opcao:
            break
        print("Opção inválida! Digite apenas um número (1, 2, 3) ou X.")
    
    if opcao == 'X':
        print("\nOperação cancelada.")
        return
    
    sistemas = {'1': 'FAT32', '2': 'exFAT', '3': 'NTFS'}
    sistema_arquivos = sistemas[opcao]
    
    if sistema_arquivos == 'FAT32' and tamanho > 32:
        print("\nAVISO: Você escolheu FAT32 para um drive de {:.1f} GB.".format(tamanho))
        print("Isso pode não funcionar devido a limitações do Windows.")
        print("\nDeseja continuar mesmo assim?")
        print("[1] SIM, tentar FAT32")
        print("[2] NÃO, cancelar")
        
        while True:
            escolha = input("\nDigite sua escolha (1 ou 2): ")
            escolha = validar_opcao(escolha, ['1', '2'])
            if escolha:
                break
            print("Opção inválida! Digite apenas 1 ou 2.")
        
        if escolha != "1":
            print("\nOperação cancelada!")
            return
    
    # Opção para o nome do volume
    print("\nNome atual do volume:", nome_atual if nome_atual else "(sem nome)")
    print("\nEscolha uma opção para o nome do volume:")
    print("[1] Manter o nome atual:", nome_atual if nome_atual else "(sem nome)")
    print("[2] Definir novo nome")
    print("[3] Sem nome")
    
    while True:
        opcao_nome = input("\nDigite sua escolha (1, 2 ou 3): ")
        opcao_nome = validar_opcao(opcao_nome, ['1', '2', '3'])
        if opcao_nome:
            break
        print("Opção inválida! Digite apenas 1, 2 ou 3.")
    
    nome_volume = None
    if opcao_nome == "1" and nome_atual:
        nome_volume = nome_atual
    elif opcao_nome == "2":
        nome_volume = input("Digite o novo nome para o volume: ")
        nome_volume = limpar_nome_volume(nome_volume)
        print(f"Nome formatado: {nome_volume}")
    
    # Confirmação
    print("\n" + "!" * 50)
    print(f"AVISO: TODOS OS DADOS NO DRIVE {drive}: SERÃO APAGADOS!")
    print(f"Sistema de arquivos selecionado: {sistema_arquivos}")
    if nome_volume:
        print(f"Nome do volume: {nome_volume}")
    else:
        print("Nome do volume: (sem nome)")
    print("!" * 50)
    print("\nEscolha uma opção:")
    print("[1] FORMATAR")
    print("[2] CANCELAR")
    
    while True:
        confirmacao = input("\nDigite sua escolha (1 ou 2): ")
        confirmacao = validar_opcao(confirmacao, ['1', '2'])
        if confirmacao:
            break
        print("Opção inválida! Digite apenas 1 ou 2.")
    
    if confirmacao != "1":
        print("\nOperação cancelada!")
        return
    
    # Executa formatação
    formatar_drive(drive, sistema_arquivos, nome_volume)
    
    input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\nErro: {str(e)}")
    finally:
        print("\nPrograma finalizado.")
