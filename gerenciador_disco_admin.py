import os
import subprocess
import string
import re
import win32api
import win32file
import win32con
import wmi
import sys
import ctypes
from ctypes import windll
from modelo import validar_opcao, limpar_nome_volume, obter_drives

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevar_privilegios():
    if not is_admin():
        print("\nEste programa precisa ser executado como administrador!")
        print("Por favor, clique com o botão direito no arquivo e selecione 'Executar como administrador'")
        input("\nPressione ENTER para sair...")
        sys.exit(1)

class GerenciadorDisco:
    def __init__(self):
        self.wmi = wmi.WMI()
    
    def obter_todos_discos(self):
        """Retorna todos os discos físicos, incluindo não alocados"""
        discos_fisicos = []
        try:
            for disco in self.wmi.Win32_DiskDrive():
                info_disco = {
                    'DispositivoID': disco.DeviceID,
                    'Modelo': disco.Model,
                    'Tamanho': float(disco.Size) / (1024**3),  # Converter para GB
                    'Status': disco.Status,
                    'Particoes': [],
                    'NaoAlocado': True
                }
                
                # Verifica partições
                for particao in self.wmi.Win32_DiskPartition():
                    if particao.DiskIndex == disco.Index:
                        info_disco['NaoAlocado'] = False
                        info_particao = {
                            'Nome': particao.Name,
                            'Tamanho': float(particao.Size) / (1024**3),
                            'Tipo': particao.Type
                        }
                        info_disco['Particoes'].append(info_particao)
                
                discos_fisicos.append(info_disco)
        except Exception as e:
            print(f"Erro ao obter informações dos discos: {str(e)}")
        
        return discos_fisicos

    def verificar_erros_disco(self, letra_drive):
        """Verifica e corrige erros no disco"""
        if not is_admin():
            elevar_privilegios()
            return False

        if not letra_drive.endswith(':'):
            letra_drive += ':'
            
        print(f"\nVerificando erros no disco {letra_drive}...")
        try:
            # Executa chkdsk para verificar erros
            cmd = f'chkdsk {letra_drive} /f /r'
            subprocess.run(cmd, shell=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro durante a verificação do disco: {str(e)}")
            return False

    def verificar_disco_sistema(self, numero_disco):
        """Verifica se o disco contém o sistema operacional"""
        try:
            # Obtém a letra do drive do Windows
            windows_drive = os.environ.get('SystemDrive', 'C:')[0]
            
            # Verifica se o disco contém partições com a letra do sistema
            for disco in self.wmi.Win32_DiskDrive():
                if disco.Index == numero_disco:
                    for particao in disco.associators("Win32_DiskDriveToDiskPartition"):
                        for drive in particao.associators("Win32_LogicalDiskToPartition"):
                            if drive.DeviceID[0].upper() == windows_drive:
                                return True
            return False
        except Exception as e:
            print(f"Erro ao verificar disco do sistema: {str(e)}")
            return True  # Por segurança, assume que é disco do sistema em caso de erro

    def inicializar_disco(self, numero_disco):
        """Inicializa um disco não alocado"""
        if not is_admin():
            elevar_privilegios()
            return False

        try:
            # Verifica se é o disco do sistema
            if self.verificar_disco_sistema(numero_disco):
                print("\n" + "!" * 80)
                print("AVISO CRÍTICO: ESTE É O DISCO DO SISTEMA!")
                print("!" * 80)
                print("\nEste disco contém o Windows e outros arquivos vitais do sistema.")
                print("Formatar este disco irá:")
                print("1. APAGAR O WINDOWS COMPLETAMENTE")
                print("2. TORNAR O COMPUTADOR INUTILIZÁVEL")
                print("3. CAUSAR PERDA PERMANENTE DE TODOS OS DADOS")
                print("\nEsta operação é EXTREMAMENTE PERIGOSA e não é recomendada!")
                
                confirmacao = input("\nTem absoluta certeza que deseja continuar? (PERIGO/N): ").upper()
                if confirmacao != "PERIGO":
                    print("\nOperação cancelada pelo usuário.")
                    return False
                
                confirmacao2 = input("\nDigite 'EU ACEITO O RISCO' em maiúsculas para prosseguir: ")
                if confirmacao2 != "EU ACEITO O RISCO":
                    print("\nOperação cancelada pelo usuário.")
                    return False
                
                print("\n" + "!" * 80)
                print("ÚLTIMA CHANCE DE CANCELAR!")
                print("!" * 80)
                confirmacao3 = input("\nDigite 'FORMATAR DISCO DO SISTEMA' para prosseguir: ")
                if confirmacao3 != "FORMATAR DISCO DO SISTEMA":
                    print("\nOperação cancelada pelo usuário.")
                    return False

            temp_dir = os.path.join(os.environ['TEMP'], 'DiskManager')
            os.makedirs(temp_dir, exist_ok=True)
            script_path = os.path.join(temp_dir, 'script_diskpart.txt')
            
            print(f"\nIniciando processo de inicialização do disco {numero_disco}...")
            print("AVISO: Este processo irá apagar todos os dados do disco!")
            print("\nATENÇÃO: Certifique-se de que:")
            print("1. O disco selecionado NÃO é o disco do sistema")
            print("2. O disco NÃO contém dados importantes")
            print("3. Você tem backup de todos os dados necessários")
            confirmacao = input("\nTem certeza que deseja continuar? (S/N): ").upper()
            
            if confirmacao != 'S':
                print("\nOperação cancelada pelo usuário.")
                return False

            # Confirmação adicional
            confirmacao2 = input("\nDigite CONFIRMAR em maiúsculas para prosseguir: ")
            if confirmacao2 != "CONFIRMAR":
                print("\nOperação cancelada pelo usuário.")
                return False
            
            # Usa diskpart para inicializar o disco
            script = f"""select disk {numero_disco}
list disk
clean
convert gpt
create partition primary
format quick fs=ntfs
assign
list volume
exit"""
            
            # Cria arquivo temporário com script diskpart
            try:
                with open(script_path, 'w') as f:
                    f.write(script)
                print(f"\nScript do diskpart criado com sucesso em: {script_path}")
            except Exception as e:
                print(f"Erro ao criar script do diskpart: {str(e)}")
                return False
            
            try:
                # Executa diskpart diretamente
                print("\nExecutando diskpart (pode demorar alguns minutos)...")
                comando = f'diskpart /s "{script_path}"'
                resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
                
                print("\nSaída do diskpart:")
                print(resultado.stdout)
                
                if resultado.returncode != 0:
                    print("\nErro ao executar diskpart:")
                    print(f"Código de retorno: {resultado.returncode}")
                    if resultado.stderr:
                        print("\nErros:")
                        print(resultado.stderr)
                    return False
                
                print("\nDiskpart executado com sucesso!")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"\nErro ao executar diskpart: {str(e)}")
                print("\nCertifique-se de:")
                print("1. O disco não está em uso por nenhum programa")
                print("2. O disco não está protegido contra gravação")
                return False
            finally:
                # Tenta remover o arquivo temporário
                try:
                    if os.path.exists(script_path):
                        os.remove(script_path)
                        print("\nArquivo temporário removido com sucesso.")
                except Exception as e:
                    print(f"\nErro ao remover arquivo temporário: {str(e)}")
        except Exception as e:
            print(f"\nErro ao inicializar disco: {str(e)}")
            return False

    def reparar_disco(self, letra_drive):
        """Repara problemas no disco"""
        if not is_admin():
            elevar_privilegios()
            return False

        if not letra_drive.endswith(':'):
            letra_drive += ':'
            
        try:
            # Primeiro, tenta reparar o sistema de arquivos
            print(f"\nTentando reparar sistema de arquivos em {letra_drive}...")
            subprocess.run(f'chkdsk {letra_drive} /f', shell=True, check=True)
            
            # Em seguida, verifica setores defeituosos
            print("\nVerificando setores defeituosos...")
            subprocess.run(f'chkdsk {letra_drive} /r', shell=True, check=True)
            
            # Por fim, otimiza o disco
            print("\nOtimizando disco...")
            subprocess.run(f'defrag {letra_drive} /O', shell=True, check=True)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro durante o reparo do disco: {str(e)}")
            return False

def mostrar_menu_principal():
    """Exibe o menu principal do gerenciador de disco"""
    print("\n" + "=" * 60)
    print("           GERENCIADOR DE DISCO AVANÇADO")
    print("=" * 60)
    print("\n1. Listar todos os discos (incluindo não alocados)")
    print("2. Verificar erros em disco")
    print("3. Reparar disco")
    print("4. Inicializar disco não alocado")
    print("5. Formatar disco (usando modelo.py)")
    print("6. Sair")
    print("\n" + "=" * 60)

def main():
    # Verifica se está rodando como administrador
    if not is_admin():
        elevar_privilegios()
        return
    
    gerenciador = GerenciadorDisco()
    
    while True:
        mostrar_menu_principal()
        opcao = input("\nEscolha uma opção (1-6): ")
        opcao = validar_opcao(opcao, ['1', '2', '3', '4', '5', '6'])
        
        if not opcao:
            print("Opção inválida! Tente novamente.")
            continue
            
        if opcao == '6':
            print("\nFinalizando programa...")
            break
            
        if opcao == '1':
            print("\nListando todos os discos...")
            discos = gerenciador.obter_todos_discos()
            print("\n" + "-" * 80)
            print("DISCOS FÍSICOS ENCONTRADOS:")
            print("-" * 80)
            
            for i, disco in enumerate(discos):
                print(f"\nDisco {i}:")
                print(f"Modelo: {disco['Modelo']}")
                print(f"Tamanho: {disco['Tamanho']:.2f} GB")
                print(f"Status: {disco['Status']}")
                print(f"Não Alocado: {'Sim' if disco['NaoAlocado'] else 'Não'}")
                
                if disco['Particoes']:
                    print("\nPartições:")
                    for part in disco['Particoes']:
                        print(f"  - {part['Nome']} ({part['Tamanho']:.2f} GB) - {part['Tipo']}")
                print("-" * 80)
                
        elif opcao == '2':
            drives = obter_drives()
            print("\nDrives disponíveis:", ', '.join(f"{d}:" for d in drives))
            drive = input("\nDigite a letra do drive para verificar (ex: C): ").upper()
            
            if drive in drives:
                gerenciador.verificar_erros_disco(drive)
            else:
                print("Drive inválido!")
                
        elif opcao == '3':
            drives = obter_drives()
            print("\nDrives disponíveis:", ', '.join(f"{d}:" for d in drives))
            drive = input("\nDigite a letra do drive para reparar (ex: C): ").upper()
            
            if drive in drives:
                gerenciador.reparar_disco(drive)
            else:
                print("Drive inválido!")
                
        elif opcao == '4':
            discos = gerenciador.obter_todos_discos()
            nao_alocados = [i for i, disco in enumerate(discos) if disco['NaoAlocado']]
            
            if not nao_alocados:
                print("\nNenhum disco não alocado encontrado!")
                continue
                
            print("\nDiscos não alocados encontrados:")
            for i in nao_alocados:
                print(f"\nDisco {i}:")
                print(f"Modelo: {discos[i]['Modelo']}")
                print(f"Tamanho: {discos[i]['Tamanho']:.2f} GB")
                
            num_disco = input("\nDigite o número do disco para inicializar: ")
            try:
                num_disco = int(num_disco)
                if num_disco in nao_alocados:
                    if gerenciador.inicializar_disco(num_disco):
                        print("\nDisco inicializado com sucesso!")
                else:
                    print("Número de disco inválido!")
            except ValueError:
                print("Entrada inválida! Digite um número.")
                
        elif opcao == '5':
            # Importa e executa o main do modelo.py
            from modelo import main as modelo_main
            modelo_main()
            
        input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\nErro: {str(e)}")
    finally:
        print("\nPrograma finalizado.")
