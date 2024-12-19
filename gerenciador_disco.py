import os
import subprocess
import string
import re
import win32api
import win32file
import win32con
import wmi
from ctypes import windll
from modelo import validar_opcao, limpar_nome_volume, obter_drives

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

    def inicializar_disco(self, numero_disco):
        """Inicializa um disco não alocado"""
        try:
            # Usa caminho absoluto para o script
            script_path = os.path.abspath(os.path.join(os.getcwd(), 'script_diskpart.txt'))
            
            print(f"\nIniciando processo de inicialização do disco {numero_disco}...")
            print("AVISO: Este processo irá apagar todos os dados do disco!")
            confirmacao = input("\nTem certeza que deseja continuar? (S/N): ").upper()
            
            if confirmacao != 'S':
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
                # Executa diskpart diretamente com privilégios elevados
                print("\nExecutando diskpart (pode demorar alguns minutos)...")
                print("Por favor, aceite a solicitação de elevação de privilégios se aparecer.")
                
                # Primeiro, lista os discos para verificar se podemos acessá-los
                subprocess.run('diskpart /? > nul', shell=True, check=True)
                print("\nAcesso ao diskpart confirmado.")
                
                # Agora executa o script
                comando = f'diskpart /s "{script_path}"'
                resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
                
                if resultado.returncode != 0:
                    print("\nErro ao executar diskpart:")
                    print(f"Código de retorno: {resultado.returncode}")
                    print("\nSaída do comando:")
                    print(resultado.stdout)
                    print("\nErros:")
                    print(resultado.stderr)
                    return False
                
                print("\nSaída do diskpart:")
                print(resultado.stdout)
                print("\nDiskpart executado com sucesso!")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"\nErro ao executar diskpart: {str(e)}")
                print("Certifique-se de:")
                print("1. Executar o programa como administrador")
                print("2. O disco não está em uso por nenhum programa")
                print("3. O disco não está protegido contra gravação")
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
