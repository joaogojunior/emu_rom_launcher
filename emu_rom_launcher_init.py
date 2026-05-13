from argparse import ArgumentParser, RawTextHelpFormatter
from os import path
import sys

from plataforma.emu_rom_launcher_win32 import detecta_servico_imdsk, inicia_imdisk_ramdisk, remove_imdisk_ramdrive
# importar dicionario de config
from cria_json_inicial.config_dict import config_dict
import valores_globais
from emu_rom_launcher_textos import description_text, epilog_text, remove_text, verbose_text, edit_gui_text, caminho_text

# import gui para editar tipo
from gui.editar_dados_tipos import JanelaEditor, QApplication

# verifica se o nome padrão não possui espaços, verifica se o caminho_arquivo existe, verifica existencia do servico
# ImDskSvc do windows para usar ramdrive, verifica se o diretorio para os arquivos temporários existe (inicializando o
# imdisk caso necessário) ou caso nao esteja disponivel checa se o diretorio para os arquivos temporario exista, se
# existir aceita e prossegue se não aborta por falta de um diretótio de destino.
def checa_caminhos_inicializacao(args):
    # testa se o nome na configuracao arquivo_rom possui algum espaco e mostra aviso
    if config_dict["arquivo_rom"].find(" ") > -1:
        print("ERRO: Escolha um nome padrão sem espaços em config.json.")
        print("Algums emuladores não aceitam espaços nos nomes de arquivo. Ex: no$msx.")
        print("Nome atual:", config_dict["arquivo_rom"])
        input("Enter para sair...")
        exit(1)
    # testa se o arquivo fornecido existe
    if not path.exists(args.caminho_arquivo):
        print("O arquivo especificado (%s) não é válido, abortando..." % args.caminho_arquivo)
        input("Enter para sair...")
        exit(1)
    # detecta o ramdrive na plataforma
    ramdrive_ok = False
    match valores_globais.PLATAFORMA:
        case "win32":
            # checa se o imdisk esta instalado... (windows)
            ramdrive_ok = detecta_servico_imdsk()
            if not ramdrive_ok:
                print("Baixe e instale o ImDsk para ter o suporte a ramdisk... Veja em: \
                https://sourceforge.net/projects/imdisk-toolkit/")
            else:
                print("Serviço do windows ImDskSvc detectado.")
        case _:
            print("Plataforma não suporta ramdrive!")
    # testa se o caminho para os arquivos temporarios existe...
    caminho_existe = path.exists(config_dict["caminho_temp_dir"])
    # caso nao exista e nao esta usando imdisk aborta...
    if not caminho_existe and not ramdrive_ok:
        print("O local especificado (%s) para os arquivos temporários não é válido, abortando..." %
              config_dict["caminho_temp_dir"])
        input("Enter para sair...")
        exit(1)
    elif not caminho_existe and ramdrive_ok:
        match valores_globais.PLATAFORMA:
            # inicia o ramdrive para as plataformas
            case "win32":
                inicia_imdisk_ramdisk()
            case _:
                # se nao tem ramdrive nao tem como continuar ja que o caminho nao existe...
                print("Plataforma não suporta ramdrive...", valores_globais.PLATAFORMA)
                input("Enter para sair...")
                exit(1)


# configura parser para lidar com parametros da linha de comando e checa se o parametro -r foi utilizado e tratando esse
# caso após checa se o arqs.caminho_arquivo foi definido e sai se nao foi.
def inicializa_e_checa_args():
    # Configuração do parser de argumentos
    parser = ArgumentParser(
        description=description_text,
        epilog=epilog_text,
        formatter_class=RawTextHelpFormatter
    )
    # Adicione o argumento opcional -r sem parâmetros
    parser.add_argument('-r', action='store_true', help=remove_text, required=False)
    # Adicione o argumento opcional -v sem parâmetros
    parser.add_argument('-v', action='store_true', help=verbose_text, required=False)
    # Adicione o argumento opcional -e sem parâmetros
    parser.add_argument('-e', action='store_true', help=edit_gui_text, required=False)
    # Adicione o argumento 'caminho_arquivo' como opcional ja que ele pode não ser fornecido quando -h ou -r for
    # utilizado
    parser.add_argument('caminho_arquivo', nargs='?', help=caminho_text)
    # Parse dos argumentos
    args = parser.parse_args()
    # checa se o parametro -r foi utilizado
    if args.r:
        match valores_globais.PLATAFORMA:
            case "win32":
                remove_imdisk_ramdrive(  )
                input("Enter para sair...")
                exit(0)
            case _:
                print("Plataforma não suporta esta operação...", valores_globais.PLATAFORMA)
    elif args.v:
        # define debug como True
        print("Habilitando mensagens debug...")
        valores_globais.debug = True
    elif args.e:
        # mostra a janela do editor e sai
        app = QApplication([])
        win = JanelaEditor()
        win.show()
        sys.exit(app.exec())
    else:
        # se -r e -h não foi especificado entao caminho_arquivo é obrigatório para operação normal
        if args.caminho_arquivo is None:
            parser.error('O caminho_arquivo é obrigatório.')
    return args
