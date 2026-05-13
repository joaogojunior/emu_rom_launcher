from sys import argv, exit
from os import path, listdir
from pyinstaller_build_date import data_hora_build
from checa_magic.classe_checa_magic import ChecaMagic

debug = True

def obtem_dados_arqumentos(entrada):
    # corrige o caso em que o ususario passa uma barra no fim mas o windows interpleta como
    # caractere de escape resultando em uma aspas dupla extra no fim da string mesmo quando
    # na linha de comando é utilizado aspas simples
    if entrada[-1] == '"':
        entrada = entrada.rstrip('"')
    # como path.split nao eh muito bom pra detectar se o caminho termina
    # com diretorio ou arquivo, temos que recorrer ao isdir pra tirar a duvida
    if path.isdir(entrada):
        caminho_fornecido = entrada
        nome_fornecido = extensao_fornecida = nome_arquivo_fornecido = ""
    else:
        # quebra parametro em caminho + nome de arquivo + nome sem extensão + extensão
        caminho_fornecido, nome_arquivo_fornecido = path.split(entrada)
        nome_fornecido, extensao_fornecida = path.splitext(nome_arquivo_fornecido)
        # a extensao so é retornada quando é um wildcard (*.bin) por exemplo
        if nome_fornecido != "*":
            extensao_fornecida = ""
    return caminho_fornecido, nome_arquivo_fornecido, nome_fornecido, extensao_fornecida

if __name__ == '__main__':
    print("detect_rom v0.1 by joaogojunior@hotmail.com lançado em:", data_hora_build)
    if len(argv) == 1:
        print("Detecta se um arquvio fornecido corresponde a algum tipo de rom reconhecido.")
        print("Erro! Forneca o caminho de um arquivo ou um wildcard para varios caminhos como parametro.")
        exit(1)

    # checa se foi passado o parametro -v que habilita as msg debug, se nao foi passado desabilita o debug
    if not "-v" in argv:
        debug = False

    # inicializa variaveis de controle
    caminho, nome_arquivo, nome, ext = obtem_dados_arqumentos(argv[1])

    # se caminho for vazio faz "."
    if caminho == "":
        caminho = "."

    # checa se caminho existe
    if not path.exists(caminho):
        # caminho nao existe..
        print("Erro! Caminho não encontrado.")
        exit(1)

    # caminho existe...
    # instancia detector de roms com as definicoes de arquivos compactados e de roms
    detetor = ChecaMagic("conf/arcs_mb.json", "conf/roms_mb.json")

    # verifica o "modo de funcionamento"
    # checa se foi fornecido um arquivo diretamente (extensao presente sinaliza wildcard):
    if nome_arquivo != "" and ext == "":
        if path.isfile(argv[1]):
            # foi fonecido um nome de arquivo entao resolve direto:
            print(argv[1] + " tipo detectado:", detetor.detecta_tipo(argv[1]))
        else:
            print("Erro: não foi possível abrir o arquivo especificado." )
            exit(1)
    else:
        # ou foi fornecido um diretorio apenas ou foi um diretorio e um wildcard
        lista_resultados = list()
        # obtem lista dos arquivos no caminho fornecido
        lista_arquivos = listdir(caminho)

        # inicializa contador de resultados
        contador_dict = {}
        contador = 0

        for nome_arquivo in lista_arquivos:
            # adiciona resultado de todos os arquivos caso ext="" ou apenas os que tem extensao especificada em ext
            if ext == "" or nome_arquivo.lower().endswith(ext.lower()):
                # reconstroi caminho para detectar arquivo
                caminho_arquivo = path.join(caminho, nome_arquivo)
                t, mb = detetor.detecta_tipo(caminho_arquivo)
                # atualiza dicionario de contador, inicializa com 0
                c = contador_dict.get(t, 0)
                c += 1
                contador_dict.update({t: c})
                if t == "Desconhecido":
                    lista_resultados.append((nome_arquivo, mb))
                else:
                    if debug:
                        print("->", mb)
                    contador += 1
                if debug:
                    print("tipo detectado:", nome_arquivo, t)
        for item in lista_resultados:
            print(item)
        print("%d arquivos conhecidos:" % contador)
        print("%d arquivos desconhecidos:" % len(lista_resultados))
        print(contador_dict)
