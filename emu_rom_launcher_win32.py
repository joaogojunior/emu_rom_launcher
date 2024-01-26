from subprocess import run as subproc_run
from msvcrt import kbhit as msvcrt_kbhit, getch as msvcrt_getch
from time import time, sleep
# importamos exit diretamente de sys pois quando compilado com pyinstaller o comando exit padrao desaparece no namespace
from sys import stdout as sys_stdout, exit
from os import path

# implementações especificas para win32 e AMD64


# detecta tecla pressionada win32
def tecla_foi_pressionada_win32():
    return msvcrt_kbhit()


# le tecla win32
def le_tecla_win32():
    return msvcrt_getch().decode("utf8")


# aguarda ate um máximo de config_dict["tempo_espera"] segundos para o ramdrive temporario ficar disponivel
# enquanto mostra contador de tempo restante, se o contador expirar encerra o programa
def aguarda_diretorio(diretorio, tempo_espera):
    tempo_inicial = time()
    continua_while = True
    while continua_while:
        tempo_passado = time() - tempo_inicial
        continua_while = tempo_passado < tempo_espera
        sys_stdout.write(f'\rTempo restante: {int(tempo_espera - tempo_passado)}'
                         f' segundos - Aguardando a unidade ficar disponivel...')
        sys_stdout.flush()
        if path.exists(diretorio):
            break
        sleep(1)
    if continua_while is False:
        print("\nTempo maximo de espera (%s s) atingido!" % str(tempo_espera))
        exit(1)
    else:
        print("\n%s está disponivel, continuando..." % diretorio)


# detecta servico do ImDskSvc utilizando sc
def detecta_servico_imdsk():
    result = subproc_run(["sc", "query", "ImDskSvc"], shell=False, capture_output=True)
    return result.returncode == 0


# inicia o ramdisk definido no caminho config_dict["caminho_temp_dir"] e tenta formatar, caso nao seja possivel abre
# dialogo do windows para formatar manualmente e espera pela unidade ficar disponivel
def inicia_imdisk_ramdisk(config_dict):
    print("Iniciando ramdisk utilizando ImDisk...")
    result = subproc_run(["imdisk", "-a", "-m", config_dict["caminho_temp_dir"], "-s",
                          config_dict["tam_ramdrive"], "-p", config_dict["format_ramdrive"]], shell=False,
                         capture_output=True)
    if result.returncode == 0:
        linhas = result.stdout.decode("cp850").split("\n")
        print("Saida imdisk :", "\n".join(linhas[:5]))
        print("fim saida imdisk.")
        # utiliza saida do imdisk para determinar se foi possível formatar o disco
        # em outras localizações do windows a mensagem será na lingua do windows
        if "Não é possível abrir o volume para acesso direto.\r" in linhas:
            print("Ramdrive %s iniciado mas não foi possível formatar, iniciando o formatador do windows..." %
                  config_dict["caminho_temp_dir"])
            print("ATENÇÃO! Formate utilizando opção FAT32 ou FAT quando a janela de formatar aparecer...")
            aguarda_diretorio(config_dict["caminho_temp_dir"], config_dict["tempo_espera_caminho"])
        else:
            print("Ramdrive %s iniciado com sucesso..." % config_dict["caminho_temp_dir"])
    else:
        print("Infelizmente nao foi possível iniciar o ramdrive, abortando...")
        print("Erro imdisk:", result.stderr.decode('cp850'))
        exit(1)


# remove a unidade ramdrive em config_dict["caminho_temp_dir"] utilizando imdisk
def remove_imdisk_ramdrive(config_dict):
    print("Tentando desmontagem padrão...")
    result = subproc_run(["imdisk", "-d", "-m", config_dict["caminho_temp_dir"]],
                         shell=False, capture_output=True)
    if result.returncode == 0:
        print("Unidade " + config_dict["caminho_temp_dir"] + " removida com sucesso.")
    else:
        print("Tentando novamente com desmontagem de emergência...")
        result = subproc_run(["imdisk", "-D", "-m", config_dict["caminho_temp_dir"]],
                             shell=False, capture_output=True)
        if result.returncode == 0:
            print("Unidade " + config_dict["caminho_temp_dir"] + " removida com sucesso.")
        else:
            print("Erro ao remover unidade:", result.stderr.decode('cp850'))
