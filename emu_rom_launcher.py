# arquivo principal do emu_rom_launcher - por joaogojunior@gmail.com
# imports principais
from tempfile import TemporaryDirectory
from os import listdir, mkdir
from typing import Any

import valores_globais

# importa todas as strings
from emu_rom_launcher_textos import creditos_text, cria_readme_txt

# descompactadores o import tem que ser o tradicional para usar getattr
import utils.descompactadores_utils as descompactadores_utils
# importa calcular_crc32
from utils.crc32_utils import calcular_crc32_arquivo

# importar classe ChecaMagic
from checa_magic.classe_checa_magic import ChecaMagic

# importar dicionario de descompactadores
from cria_json_inicial.descompactadores_dict import descompactadores

# importar dicionario de arcs_mv
from cria_json_inicial.arcs_mb_dict import arcs_mb_dict

# importrar escolha manual
from utils.escolha_manual_utils import escolha_manual, pergunta_escolha_manual

from emu_rom_launcher_init import inicializa_e_checa_args, checa_caminhos_inicializacao
from utils.arquivo_util import lista_todos_arquivos_no_caminho, copia_arquivo
from criador_json.criador_json import escreve_json_padrao, carrega_config

# realiza imports adicionais especificos da plataforma
if valores_globais.PLATAFORMA == 'win32':
    # import especifico do windows
    print("Plataforma Windows detectada...")
    from plataforma.emu_rom_launcher_win32 import *

# lista de chaves que não são aplicáveis selecionadas pelo usuario
lista_nao_aplicavel = list()

# determina o tipo de arquivo a partir do nome do arquivo
def tipo_do_nome_arquivo(caminho_arquivo, lista_encontrados=None):
    global lista_nao_aplicavel
    # extrai o nome de arquivo do caminho completo fornecido (esse caminho ou veio da
    # da linha de comando ou de um arquivo comprimido e pode conter um caminho prefixado
    nome_arquivo = path.basename(caminho_arquivo)
    extensao = path.splitext(str(nome_arquivo))[1].lower()
    # se nao foi fornecido uma lista cria uma nova ou usa a fornecida
    lista_encontrados = list() if lista_encontrados is None else lista_encontrados[:]
    # filtrado de chaves excluindo as em lista_nao_aplicavel e checando a chave 'ext' do
    # dicionario se contem o nome de arquivo ou a extensão dele em minusculas
    # inicializa lista_chaves que vai conter as chaves encontradas
    lista_chaves = list()
    for chave_filtrada in set(valores_globais.dados_tipo.keys()) - set(lista_nao_aplicavel):
        # checa se o nome de arquivo ou se a extensão dele existe na lista em 'ext'
        # em minusculas
        arquivos_ou_extensoes_permitidas = valores_globais.dados_tipo[chave_filtrada]['ext']
        if valores_globais.debug:
            print("Extensão do arquivo:", extensao)
            print("Extensões para o tipo testado:", arquivos_ou_extensoes_permitidas)
        if nome_arquivo.lower() in arquivos_ou_extensoes_permitidas or extensao in arquivos_ou_extensoes_permitidas:
            # adiciona chave a lista de chaves possiveis
            # desligando esse if para ver se consigo melhorar a interacao no modo manual
            # if not valores_globais.manual:
            if valores_globais.debug:
                print("Candidato a chave encontrada:", chave_filtrada)
            lista_chaves.append(chave_filtrada)
    # Inicializa chave_retorno
    chave_retorno = "Desconhecido"
    if len(lista_chaves) == 0 and valores_globais.manual:
        chave_retorno = seleciona_tipos_modo_manual(caminho_arquivo, [])
    if len(lista_chaves) == 1:
        if valores_globais.manual:
            # pergunta ao usuario mesmo assim
            chave_retorno = seleciona_tipos_modo_manual(caminho_arquivo, lista_chaves)
        else:
            # retorna elemento encontrado
            if valores_globais.debug:
                print("Chave encontrada:", lista_chaves[0])
            chave_retorno = lista_chaves[0]
    elif len(lista_chaves) > 1:
        # se escolha manual estiver habilitada pula esse bloco
        if not valores_globais.manual:
            # ha muitos candidatos a chaves corretas
            # se ja exite alguma das escolhas possiveis entre os items em lista_encontrados, assume este como correto
            # tambem para o arquivo atual.
            # ... e se lista_encontrados foi passada e contem itens
            chave_retorno = encontra_chave_tipo_ja_selecionado("Desconhecido", lista_chaves, lista_encontrados)
            # tem que ser a ultima opcao - performance mais baixa
            # testa se apenas uma entre as chaves entre lista_chaves inicia com "*"
            if chave_retorno == "Desconhecido":
                lista_chaves_padrao = [chave for chave in lista_chaves if chave.startswith("*")]
                if len(lista_chaves_padrao) == 1:
                    if valores_globais.debug:
                        print("Encontrado chave com valor padrão:",lista_chaves_padrao[0])
                    chave_retorno = lista_chaves_padrao[0]
        if chave_retorno == "Desconhecido":
            # recorrendo a escolha manual...
            # comportamento aqui muda se estiver no modo manual global
            if valores_globais.manual:
                chave_retorno = seleciona_tipos_modo_manual(caminho_arquivo, lista_chaves)
            else:
                print("Determine o tipo de %s:" % caminho_arquivo)
                escolha = escolha_manual(lista_chaves, "Nenhum destes.")
                # checa se escolha e a opcao não aplicavel
                if escolha == "Nenhum destes.":
                    # se for adiciona lista_chaves a lista_nao_aplicavel e retorna "Desconhecido"
                    lista_nao_aplicavel += lista_chaves
                    # return "Desconhecido"
                else:
                    chave_retorno = escolha
    return chave_retorno


def encontra_chave_tipo_ja_selecionado(valor_padrao_retorno, lista_chaves, lista_encontrados):
    if valores_globais.debug:
        print("iniciando encontra_chave_tipo_ja_selecionado:")
        print(valor_padrao_retorno, lista_chaves, lista_encontrados)
    if len(lista_encontrados) > 0:
        for chave in lista_chaves:
            # checa se ja existe em alguma das escolhas a mesma chave
            if any(chave == chave_ja_detectada for _, chave_ja_detectada in lista_encontrados):
                # se tiver a chance é muito alta a chance desta ser a escolha correta
                if valores_globais.debug:
                    print("item escolhido por ter mesmo tipo encontrado anteriormente:", chave)
                valor_padrao_retorno = chave
                break
    return valor_padrao_retorno


# funcao que executa o comando personalizado em "cmd", inicialmente checa se o valor de "dos" é verdadeiro se for
# modifica caminho_arquivo para que o nome e diretorio do arquivo nao ultrapasse 8 caracteres emulando o estilo do
# win95 adicionando ~1 no fim do nome. Em seguida checa todos os argumentos em "cmd" pelos caracteres especiais
# "?c", "?d", "?D" e "?a" significando o nome do arquivo com caminho completo, caminho do diretorio relativo ao
# diretorio temporário, caminho do diretório completo temporário e nome do alvo encontrado, se não houver caracteres
# especiais o caminho completo mais nome do arquivo rom é adicionado como último parâmetro de "cmd".
def executar_comando_para_tipo_arquivo(tipo_arquivo, destino_dir, destino_nome_arquivo, lista_nome_crc32=None, alvo=""):
    # salva drive
    drive_caminho_arquivo = path.splitdrive(destino_dir)[0]
    # checa se os nomes tem que ser compatives com dos
    dos = valores_globais.dados_tipo[tipo_arquivo]['dos']
    print("Nomes de arquivos compatível com DOS:", dos)
    # se dos estiver setado ajusta tamanho do diretorio e do nome do arquivo
    if dos:
        print("Truncando nomes para DOS...")
        # rescreve valores em destino_dir e destino_nome para valores compativeis com dos
        # inicializa caminho_compativel_com_dos com uma copia da unidade de caminho_arquivo
        destino_dir = gera_caminho_compativel_com_dos(drive_caminho_arquivo[:], destino_dir)
        print("caminho_compativel_com_dos:", destino_dir)
        destino_nome_arquivo = gera_nome_arquivo_compativel_com_dos(destino_nome_arquivo)
    print("Configurando comando para:", tipo_arquivo)
    argumentos = valores_globais.dados_tipo[tipo_arquivo]['cmd']
    # substitui marcadores ex "?a" nos parametros
    adicionado_ok = substitui_marcadores_argumentos(alvo, argumentos, destino_dir, destino_nome_arquivo,
                                                    drive_caminho_arquivo, lista_nome_crc32, tipo_arquivo)
    # checa se ja adicionou o caminho ou diretorio nos parametros
    if not adicionado_ok:
        destino = '"' + str(path.join(destino_dir, destino_nome_arquivo)) + '"'
        # como nao encontrou os marcadores especiais nos parametros adiciona caminho_arquivo como ultimo parametro
        print('Adicinando', destino, "como último parametro.")
        argumentos.append(destino)
    # Executa o comando
    print("comando:", " ".join(argumentos))
    try:
        # subproc_run(" ".join(argumentos), shell=True)
        # pass
        run_and_get_retval_stdout(" ".join(argumentos))
    except FileNotFoundError:
        print("Não foi possível encontrar o comando %s, verifique a configuração para este tipo..." % argumentos[0])


def substitui_marcadores_argumentos(alvo, argumentos, destino_dir, destino_nome_arquivo, drive_caminho_arquivo,
                                    lista_nome_crc32, tipo_arquivo):
    # marcadores válidos:
    # ?a - alvo (apenas nome do arquivo)
    # ?A - albo (apenas nome do arquivo sem extensão)
    # ?*substring* - arquivo unico em lista_nome_crc32 que possia "substring" no nome, se houver mais aborta.
    # ?d - diretorio alvo relativo
    # ?D - diretorio alvo completo
    # ?t - diretorio temporario relativo
    # ?T - diretorio temporario completo
    # ?c - caminho completo com nome de arquivo
    # ?u - drive temporário sem barra
    # ?U - drive temporário com barra
    print("Procurando marcadores nos argumentos... (" + str(len(argumentos)) + " argumentos)")
    # esta for passa por todos os argumentos do ultimo ate o primeiro
    adicionado_ok = False
    for indice_param in range(len(argumentos) - 1, -1, -1):
        # checa se o arqumento inicia com "caminho:"
        if argumentos[indice_param].startswith("caminho:"):
            # se iniciar busca o caminho no caminhos e substitui
            chave_caminho = argumentos[indice_param][8:]
            caminho = ""
            try:
                caminho = valores_globais.caminhos[chave_caminho]
            except KeyError:
                print(f"Erro ao substituir o caminho ({chave_caminho}), chave não encontrada.")
                print("Verifique a seção 'caminhos' em dados_tipo.json.")
                exit(1)
            print(f"caminhos[{chave_caminho}] = {caminho}")
            argumentos[indice_param] = caminho
        else:
            # procura por ? na string e trata de acordo.
            indice_marcador = argumentos[indice_param].find('?')
            while indice_marcador > -1:
                # parametro possui ao menos um ? entao verifica proximo caractere:
                match argumentos[indice_param][indice_marcador + 1]:
                    case "a":
                        if alvo == "":
                            print("Aviso: Injetando ?a mas o alvo é \"\", usando o nome de arquivo em destino_nome_arquivo")
                            alvo = destino_nome_arquivo
                        # substitui por alvo
                        print("Injetando " + alvo + " no parametro " + str(indice_param - 1) + "...")
                        argumentos[indice_param] = argumentos[indice_param].replace('?a', alvo, 1)
                        # procura novamente
                        indice_marcador = argumentos[indice_param].find('?')
                        adicionado_ok = True
                    case "A":
                        if alvo == "":
                            print("Aviso: Injetando ?A mas o alvo é \"\", usando o nome de arquivo em destino_nome_arquivo")
                            alvo = destino_nome_arquivo
                        # substitui por alvo sem extensão
                        alvo_sem_ext = str(path.splitext(alvo)[0])
                        print("Injetando " + alvo_sem_ext + " no parametro " + str(indice_param - 1) + "...")
                        argumentos[indice_param] = argumentos[indice_param].replace('?A', alvo_sem_ext, 1)
                        # procura novamente
                        indice_marcador = argumentos[indice_param].find('?')
                        adicionado_ok = True
                    case "*":
                        if lista_nome_crc32 is not None:
                            # substitui por arquivo unico existente entres os arquivos copiados no ramdrive
                            # que satisfaca a cadeia.
                            # encontra index de ?*
                            marcador_inicial = argumentos[indice_param].find('?')
                            # encontra index do * final
                            marcador_final = argumentos[indice_param].find('*', marcador_inicial + 2)
                            # extrai o wildcard que esta no intervalo encontrado
                            wildcard = argumentos[indice_param][marcador_inicial + 2:marcador_final]
                            # encontra arquivo com base no wildcard
                            arquivos_encontrados = [f for f in lista_nome_crc32[0] if wildcard in f.lower()]
                            if len(arquivos_encontrados) > 1:
                                print(tipo_arquivo)
                                print(
                                    "Erro: o wildcard configurado em %s especifica mais de um arquivo, por favor revise." %
                                    argumentos[indice_param])
                                if bool(valores_globais.config_dict["enter_para_fechar"]):
                                    input("Enter para sair...")
                                exit(1)
                            # injetando arquivo encontrado com wildcard no parametro correto
                            print("Injetando " + arquivos_encontrados[0] + " no parametro " + str(indice_param - 1) + "...")
                            argumentos[indice_param] = argumentos[indice_param].replace('?*' + wildcard + "*",
                                                                                        arquivos_encontrados[0], 1)
                            # procura novamente
                            indice_marcador = argumentos[indice_param].find('?')
                            adicionado_ok = True
                        else:
                            print("Erro - Não é possivel usar ?*..* fora de um arquivo compactado.")
                            if bool(valores_globais.config_dict["enter_para_fechar"]):
                                input("Enter para sair...")
                            exit(1)
                    case "c":
                        # substitui por caminho absoluto com nome de arquivo
                        destino = str(path.join(destino_dir, destino_nome_arquivo))
                        print("Injetando " + destino + " no parametro " + str(indice_param - 1) + "...")
                        argumentos[indice_param] = argumentos[indice_param].replace('?c', destino, 1)
                        # procura novamente
                        indice_marcador = argumentos[indice_param].find('?')
                        # terminamos com o loop
                        # break
                        adicionado_ok = True
                    case "d":
                        # substitui por diretorio sem drive e sem o nome de arquivo
                        diretorio_relativo = str(path.splitdrive(destino_dir)[1])
                        print("Injetando " + diretorio_relativo + " no parametro " +
                              str(indice_param - 1) + "...")
                        argumentos[indice_param] = argumentos[indice_param].replace('?d', diretorio_relativo, 1)
                        # procura novamente
                        indice_marcador = argumentos[indice_param].find('?')
                        # terminamos com o loop
                        # break
                        adicionado_ok = True
                    case "D":
                        # substitui por diretorio com drive e sem o nome de arquivo
                        print("Injetando " + destino_dir + " no parametro " +
                              str(indice_param - 1) + "...")
                        argumentos[indice_param] = argumentos[indice_param].replace('?D', destino_dir, 1)
                        # procura novamente
                        indice_marcador = argumentos[indice_param].find('?')
                        # terminamos com o loop
                        adicionado_ok = True
                    case "t":
                        # substitui por diretorio sem drive e sem o nome de arquivo
                        diretorio_relativo = str(path.splitdrive(destino_dir)[1])
                        qtd = len(diretorio_relativo.split(path.sep))
                        if qtd > 1:
                            diretorio_relativo = diretorio_relativo.split(path.sep)[0]
                        print("Injetando " + diretorio_relativo + " no parametro " +
                              str(indice_param - 1) + "...")
                        argumentos[indice_param] = argumentos[indice_param].replace('?t', diretorio_relativo, 1)
                        # procura novamente
                        indice_marcador = argumentos[indice_param].find('?')
                        # terminamos com o loop
                        # break
                        adicionado_ok = True
                    case "T":
                        destino_dir_temp = destino_dir[:]
                        qtd = len(destino_dir.split(path.sep))
                        if qtd > 2:
                            destino_dir_temp = str(path.sep.join(destino_dir.split(path.sep)[:2]))
                        # substitui por diretorio com drive e sem o nome de arquivo
                        print("Injetando " + destino_dir_temp + " no parametro " +
                              str(indice_param - 1) + "...")
                        argumentos[indice_param] = argumentos[indice_param].replace('?T', destino_dir_temp, 1)
                        # procura novamente
                        indice_marcador = argumentos[indice_param].find('?')
                        # terminamos com o loop
                        adicionado_ok = True
                    case "u":
                        # substitui por drive temporario sem barra
                        print("Injetando " + drive_caminho_arquivo + " no parametro " + str(indice_param - 1) + "...")
                        argumentos[indice_param] = argumentos[indice_param].replace('?u', drive_caminho_arquivo, 1)
                        # procura novamente
                        indice_marcador = argumentos[indice_param].find('?')
                        # terminamos com o loop
                        adicionado_ok = True
                    case "U":
                        # substitui por drive temporario com barra
                        # obs barra "/" nao precisa ser "escapada" e funciona igualmente no dosbox
                        # do windows e do linux, entao é a escolha apropriada.
                        path_sep = "/"
                        print("Injetando " + drive_caminho_arquivo + path_sep + " no parametro " + str(
                            indice_param - 1) + "...")
                        argumentos[indice_param] = argumentos[indice_param].replace('?U', drive_caminho_arquivo + path_sep,
                                                                                    1)
                        # procura novamente
                        indice_marcador = argumentos[indice_param].find('?')
                        # terminamos com o loop
                        adicionado_ok = True
                    case _:
                        # comando mal formado:
                        print("Erro: Argumento mal formado. %s - (posição: %d)" %
                              (argumentos[indice_param], indice_marcador + 1))
                        if bool(valores_globais.config_dict["enter_para_fechar"]):
                            input("Enter para sair...")
                        exit(1)
    return adicionado_ok


def gera_caminho_compativel_com_dos(caminho_compativel_com_dos, destino):
    # o valor caminho_compativel_com_dos pode conter um valor inicial
    # o split em [3:] eh para remover o drive e fatia por dir
    for diretorio in destino[3:].split("\\"):
        temp_nome = gera_nome_arquivo_compativel_com_dos(diretorio)
        caminho_compativel_com_dos += "\\" + temp_nome
        print(diretorio, temp_nome)
    return caminho_compativel_com_dos


def gera_nome_arquivo_compativel_com_dos(nome_arquivo):
    # remove outros caracteres nao permitidos
    caracteres_nao_permitidos = [" ", "[", "]"]
    for c in caracteres_nao_permitidos:
        nome_arquivo = nome_arquivo.replace(c, "")
    temp_nome, temp_ext = path.splitext(nome_arquivo)
    print(temp_nome, temp_ext)
    usa_tilde = False
    if temp_ext:
        if len(temp_ext) > 4:
            temp_ext = temp_ext[:4]
            usa_tilde = True
    if len(temp_nome) > 8 or usa_tilde:
        temp_nome = temp_nome[:6] + "~1"
    return temp_nome + temp_ext


# funcao copia a rom a ser executada para um diretorio temporario com um nome definido por "arquivo_rom" em config.json
# ou uma versao do nome do arquivo original substituindo os espaços por "_" e executa o comando associado com o
# tipo_arquivo. Ao fim, checa se algum arquivo foi adicionado ou alterado e salva esses arquivos, se existirem,
# no diretorio ./saves com o nome original do arquivo mais "_save_XXX.tar.xz" onde XXX é um número que
# inicia em 000 e vai incrementado caso já esteja utilizado..
# Se descompactador for None nao extrai arquivos e parâmetro alvo nao precisa ser especificado podendo apenas ter valor
# "" e apos copia o arquivo apontado por caminho_arquivo para o diretorio temporário utilizando o nome previamente definido.
# Se descompactador for especificado verifica o valor de "extrai_tudo".
# Se falso utiliza o alvo e o tipo de arquivo ja definidos anteriormente e descompacta o alvo no diretorio temporario
# criando um arquivo com nome definido anteriormente.
# Se o valor de "extrai_tudo" for verdadeiro extrai todos arquivos do arquivo compactado no diretorio temporario.
# Chama executar_comando_para_tipo_arquivo() para que o comando personalizado para o tipo_arquivo seja
# executado para o arquivo em destino.
# Por fim se tiver extraido tudo verifica por arquivo novos ou alterados no ramdrive e salva eles em ./saves caso
# existam.
def popula_ramdrive_e_executa_alvo(caminho_arquivo, tipo_arquivo, descompactador=None, alvo="",
                                   listas_nome_crc32=None, arquivo_salvo=None):
    # no minimo esta funcao recebe dois parametros:
    # caminho_arquivo - caminho completo fornecido pelo usuario
    # tipo_arquivo - chave do dicionario para o tipo detectado ou "Desconhecido" se nao detectado
    # mas se for utilizado com arquivos compactados ai utiliza os seguintes variaveis
    # descompactador = handler para o descompactador correto
    # alvo = string do caminho relativo interno mais nome do alvo selecionado dentro do arquivo comprimido
    # listas_nome_crc32 = listas de arquivos e crc32 de cada arquivo dentro do arquivo comprimido
    # arquivo_salvo = arquivo que vai guardar as alteracoes realizadas nos arquivos extraidos
    #   enquanto estavam no ramdrive

    # variavel que define se todos os arquivos serão descompactados ou apenas o alvo fornecido.
    extrai_tudo = valores_globais.dados_tipo[tipo_arquivo]["extrai_tudo"]
    if valores_globais.debug:
        print("Extrai todos arquivos:", extrai_tudo)
    novo_alvo = ""

    # primeiramente checa se foi chamado com descompactador assim pre processa algumas veriaveis
    # de acordo
    if descompactador is None:
        # nao foi passado descompactador logo apenas caminho_de_arquivo e tipo_de_arquivo disponiveis
        # inicializa variavel
        caminho_relativo_alvo = ""
    else:
        # checa se existem separadores de diretorios extras que viriam do arquivo compactado
        # em alvo, remove o caminho extra de alvo e retorna como caminho_relativo_alvo
        novo_alvo, caminho_relativo_alvo = checa_presenca_separadores_diretorios_extras(alvo, caminho_arquivo)
    # se houver alvo escolhe ele, mas se nao houver usa o nome de arquivo em caminho_arquivo
    # fornecido pelo usuario
    destino_nome_arquivo = str(novo_alvo[:]) if novo_alvo != "" else str(path.basename(caminho_arquivo))

    # substitui espacos por _ em destino_nome_arquivo se configurado e estiver
    # operando em um arquivo compactado
    # resolve typing do parametro nome_alterado evitando uso de bytes implicito
    # necessario em alguns casos como no no$msx
    if bool(valores_globais.config_dict["converte_espacos_em_underscore"]) and descompactador:
        destino_nome_arquivo = str(destino_nome_arquivo.replace(" ", "_"))

    # variável destino guarda valor do caminho no diretorio temporario mais nome do arquivo a ser escrito, porém quando
    # todos os arquivos existentes no arquivo compactado serão extraídos utiliza apenas o dirname de destino (o caminho
    # no diretorio temporario)
    # Cria um diretório temporário no RAM drive
    with (TemporaryDirectory(dir=valores_globais.config_dict["caminho_temp_dir"]) as temp_dir):
        # caminho relativo alvo pode estar vazio
        # define destino_dir como o caminho temporario mais o caminho relativo alvo se houver
        if caminho_relativo_alvo != "" and extrai_tudo:
            destino_dir = path.join(temp_dir, caminho_relativo_alvo)
        else:
            destino_dir = temp_dir[:]
        # se "arquivo_rom" esta definido e nao extrai tudo
        if valores_globais.config_dict["arquivo_rom"] != "" and not extrai_tudo:
            # se "arquivo_rom" for definido, utiliza o nome padrão com extensão original
            # do alvo em minusculas
            ext = path.splitext(destino_nome_arquivo)[1].lower()
            destino_nome_arquivo = valores_globais.config_dict["arquivo_rom"] + ext
        # checa se é necessário descompactar o arquivo antes
        if descompactador is None:
            if not extrai_tudo:
                # não é necessário descompactar, arquivo rom foi especificado diretamente
                # copia arquivo para diretorio temporario
                copia_arquivo(caminho_arquivo, path.join(destino_dir, destino_nome_arquivo))
            else:
                # nao é necessario descompactar isso ja foi feito,
                # copia todos os arquivos no caminho de caminho_arquivo
                # que possuam ou contenham o nome do arquivo de destino
                # no inicio do seu proprio nome para o ramdrive. (para conseguir
                # copiar todas as faixas de um cd ripado por exemplo, cujo o nome
                # no arquivo .cue esta no inicio de cada arquivo bin de faixa)
                # lista arquivos existentes no caminho
                if valores_globais.debug:
                    print("Caminho origem copia:", path.dirname(caminho_arquivo))
                lista_arquivos_copiar = lista_todos_arquivos_no_caminho(path.dirname(caminho_arquivo), relativo=True,
                                                                        inclui_subdirs=False)
                nome_arquivo = path.splitext(destino_nome_arquivo)[0]
                lista_arquivos_copiar = [f for f in lista_arquivos_copiar if f.startswith(nome_arquivo)]
                if valores_globais.debug:
                    print("Arquivos a serem copiados:", lista_arquivos_copiar)
                # copia todos os arquivos selecionados acima em destino_dir
                for c in range(len(lista_arquivos_copiar)):
                    x = lista_arquivos_copiar[c]
                    # verifica se precisa converter o nome do alvo (destino_nome_arquivo)
                    if x == destino_nome_arquivo:
                        if bool(valores_globais.config_dict['converte_espacos_em_underscore']) and destino_nome_arquivo.find(" ") > -1:
                            destino_nome_arquivo = destino_nome_arquivo.replace(" ", "_")
                        # atualiza item na lista para compatibilidade com "?*..*"
                        lista_arquivos_copiar[c] = destino_nome_arquivo
                        copia_arquivo(path.join(str(path.dirname(caminho_arquivo)), x), path.join(destino_dir, destino_nome_arquivo))
                    else:
                        copia_arquivo(path.join(str(path.dirname(caminho_arquivo)), x), path.join(destino_dir, x))
                # como lista_nome_crc32 aqui eh vazio vou passar essa lista no lugar dele
                # para compatibilizar comandos que utilizam a lista como o ?*..*
                listas_nome_crc32 = [lista_arquivos_copiar, list()]
                if valores_globais.debug:
                    print("lista_nome_crc33 atualizada:", listas_nome_crc32)
        else:
            # foi especificado um arquivo compactado...
            # checa se extrairemos apenas o alvo ou se extrairemos tudo
            if not extrai_tudo:
                # extrai alvo no ram_drive
                # aqui a raiz de extracao de arquivos compactados é sempre temp_dir
                # alvo original é necessario para extracao de arquivo
                descompactador(caminho_arquivo, temp_dir, destino_nome_arquivo, alvo)
                print(f"Arquivo extraído em: {path.join(temp_dir, destino_nome_arquivo)}")
            else:
                # extrai todos arquivos no ram_drive em temp_dir
                # adiciona "\" ou "/" ao fim do diretorio dependendo do padrao do os...
                descompactador(caminho_arquivo, temp_dir)
                print(f"extraindo todos os aqruivos em: {destino_dir}")
        # checa se carrega algum arquivo salvo
        if extrai_tudo and arquivo_salvo is not None:
            print("extraindo arquivo salvo %s em %s..." % (arquivo_salvo, temp_dir))
            descompactadores_utils.descompactar_tar_xz(arquivo_salvo, path.join(temp_dir, ""), "")
        # executa o comando correspondente ao tipo de arquivo
        executar_comando_para_tipo_arquivo(tipo_arquivo, destino_dir, destino_nome_arquivo, listas_nome_crc32, str(novo_alvo))
        # se foi extraido algum arquivo, verifica se houve alteracoes
        if extrai_tudo and descompactador is not None:
            salva_arquivos_novos_ou_alterados(arquivo_salvo, caminho_arquivo, listas_nome_crc32, temp_dir)
        # se estivermos no modo manual e nao existe arquivo do historico de execucao cria um
        if valores_globais.manual == True and not alvo == "" and not checa_historico_execucao_existe(caminho_arquivo):
            cria_historico_execucao(caminho_arquivo, alvo, tipo_arquivo)
        if bool(valores_globais.config_dict["enter_para_fechar"]):
            input("Enter para sair...")
        print("Aguarde enquanto o diretório temporário é removido...")

def obtem_caminho_historico(caminho_arquivo):
    dir_historico = path.join(".", "historico")
    if not path.isdir(dir_historico):
        print(f"Caminho {dir_historico} não existe, criando agora...")
        mkdir(dir_historico)
    nome_arquivo_historico = f"hist_{path.basename(caminho_arquivo)}.json"
    return path.join(dir_historico, nome_arquivo_historico)

def checa_historico_execucao_existe(caminho_arquivo):
    return path.exists(obtem_caminho_historico(caminho_arquivo))

def cria_historico_execucao(caminho_arquivo, alvo, tipo_arquivo):
    caminho_historico = obtem_caminho_historico(caminho_arquivo)
    dict_hist = {
        path.basename(caminho_arquivo): (alvo, tipo_arquivo)
    }
    print("Criando historico de execucao:", dict_hist)
    escreve_json_padrao(caminho_historico, dict_hist)

def carrega_historico_execucao(caminho_arquivo):
    caminho_historico = obtem_caminho_historico(caminho_arquivo)
    if checa_historico_execucao_existe(caminho_arquivo):
        dict_hist, ver = carrega_config(caminho_historico)
        return dict_hist[path.basename(caminho_arquivo)]
    return "", ""

def checa_presenca_separadores_diretorios_extras(alvo, caminho_arquivo):
    # inicializa algumas variaveis
    caminho_relativo_alvo = ""
    index_separador_windows = alvo.rfind("\\")
    index_separador_linux = alvo.rfind("/")
    # se nao foi especificado faz alvo ser o nome (basename) de caminho_arquivo
    if alvo == "":
        alvo = path.basename(caminho_arquivo)
    # checa se alvo foi especificado mas tem um caminho alem do nome de arquivo
    # as vezes arquivos comprimidos permitem que o separador seja / mesmo no
    # windows como no caso do zip.
    elif index_separador_windows > -1:
        # corrige o caso contrario, de um arquivo vir com o separador // mas o ambiente
        # nao eh windows, converte para unix/linux
        if valores_globais.PLATAFORMA != "win32":
            # se for linux altere todas as ocorrencias de \ em /
            alvo = alvo.replace("\\", "/")
        # alvo eh caminho composto com seu proprio caminho relativo, extrai agora:
        caminho_relativo_alvo, alvo = path.dirname(alvo), path.basename(alvo)
    elif index_separador_linux > -1:
        # corrige o caso de separador / no caminho de alvo mas o sistema eh windows
        if valores_globais.PLATAFORMA == "win32":
            # se for windows altere todas as ocorrencias de / em \
            alvo = alvo.replace("/", "\\")
        # alvo eh caminho composto com seu proprio caminho relativo, extrai agora:
        caminho_relativo_alvo, alvo = path.dirname(alvo), path.basename(alvo)
    return alvo, caminho_relativo_alvo


# salva arquivos novos ou alterados em um savefile em "./saves" o nome do save file eh gerado
# incrementando a partir de .\saves\"path.basename(caminho_arquivo)"_save_000.tar.xz
def salva_arquivos_novos_ou_alterados(arquivo_salvo, caminho_arquivo, listas_nome_crc32, temp_dir):
    lista_arquivos_para_guardar = procura_arquivo_adicionado_ou_alterado(listas_nome_crc32, temp_dir)
    if len(lista_arquivos_para_guardar) > 0:
        print("lista de arquivos novos e alterados:", lista_arquivos_para_guardar)
        # criar um arquivo compactado com as alterações
        saves_dir = path.join(".", "saves")
        # cria diretorio para guardar os saves
        if not path.exists(saves_dir):
            print("criando %s..." % saves_dir)
            mkdir(saves_dir)
        if arquivo_salvo is None:
            nome_arquivo = encontra_proximo_nome_disponivel(caminho_arquivo, saves_dir)
        elif bool(valores_globais.config_dict["salvar_mesmo_arquivo"]):
            nome_arquivo = arquivo_salvo
        elif escolha_manual(["Utilizar mesmo arquivo de save (%s)" % arquivo_salvo],
                            "Criar novo arquivo save") != "Criar novo arquivo save":
            nome_arquivo = arquivo_salvo
        else:
            nome_arquivo = encontra_proximo_nome_disponivel(caminho_arquivo, saves_dir)

        print("salvando alterações para o arquivo:", nome_arquivo)
        # cria arquivo compactado de nome nome_arquivo em saves_dir
        descompactadores_utils.criar_tar_xz(nome_arquivo, lista_arquivos_para_guardar, temp_dir)


def encontra_proximo_nome_disponivel(caminho_arquivo, saves_dir):
    # procura um nome de arquivo novo
    contador = 0
    while True:
        nome_arquivo = path.join(saves_dir, path.basename(caminho_arquivo) + "_save_%.3d.tar.xz"
                                 % contador)
        if not path.exists(nome_arquivo):
            break
        contador += 1
    return nome_arquivo


# metodo que checa se algum arquivo foi criado ou alterado e retorna uma lista desses arquivos.
def procura_arquivo_adicionado_ou_alterado(listas_nome_crc32, temp_dir):
    # cria um set a partir da lista de nomes em lista_nomes_crc32[0]
    arquivos_no_zip = set(listas_nome_crc32[0])
    if valores_globais.debug:
        print("Lista dos arquivos comprimidos:", arquivos_no_zip,  len(arquivos_no_zip))
    # print("arquivos_no_zip:", arquivos_no_zip)
    # coleta todos nomes dos arquivos no temp_dir mas reformata os caminhos para serem relativos e usarem / como
    # separador
    arquivos_no_diretorio = lista_todos_arquivos_no_caminho(temp_dir, relativo=True, posix=True)
    # cria o set a partir da lista encontrada
    arquivos_no_diretorio = set(arquivos_no_diretorio)
    if valores_globais.debug:
        print("Lista dos arquivos extraidos:", arquivos_no_diretorio, len(arquivos_no_diretorio))
    # print("arquivos_no_diretorio:", arquivos_no_diretorio)
    # Arquivos novos é calculado subtraindo o set em arquivos_no_zip do set arquivos_no_diretorio, guarda resultado
    # como uma lista
    # arquivos_novos = list(arquivos_no_diretorio - arquivos_no_zip)
    arquivos_novos = [arquivo for arquivo in arquivos_no_diretorio.difference(arquivos_no_zip)]
    if valores_globais.debug:
        print("Arquivos_novos:", arquivos_novos)
    # Arquivos alterados é uma lista criada a partir da interseção de arquivos_no_diretorio e arquivos_no_zip onde cada
    # elemento foi adicionado porque seu crc32 atual nao bateu com o crc32 calculado antes da execução.
    # print("listas_nome_crc32:", listas_nome_crc32)
    arquivos_alterados = [arquivo for arquivo in arquivos_no_diretorio.intersection(arquivos_no_zip)
                          if calcular_crc32_arquivo(path.join(temp_dir, arquivo)) !=
                          listas_nome_crc32[1][listas_nome_crc32[0].index(arquivo)]]

    if valores_globais.debug:
        print("arquivos_alterados:", arquivos_alterados)
    # tudo foi convertido em listas pois sets so podem ser subtraido e nao somados.
    return arquivos_novos + arquivos_alterados


# metodo que auxilia a encotrar possiveis alvos no arquivo compactado, se a lista de alvos for maior que 1 tenta
# definir o alvo correto por heuristica ou escolha manual caso não seja possivel diretamente, se for 0 sai do
# programa. O tipo de arquivo precisa existir no dicionario de descompactadores com uma função para extrair deste tipo
# de arquivo compactado e uma função que possa listar os conteúdos do arquivo compactado
def fase3_encontra_e_processa_alvos(caminho_arquivo, ext_arquivo):
    # inicializa diversas variáveis
    # valor inicial tipo_arquivo
    chave_alvo = "Desconhecido"
    alvo = ""

    existe_historico = checa_historico_execucao_existe(caminho_arquivo)

    # obtem lista de arquivos dentro do arquivo comprimido contendo (nome, tipos detectados e
    # o crc32) e o handler para o decompressor
    descompactador_handler, listas_nome_crc32_tipos = coleta_lista_arquivos_comprimidos(caminho_arquivo, ext_arquivo, not existe_historico)

    # checa se existe algum historico de execucao
    if existe_historico:
        alvo, chave_alvo = carrega_historico_execucao(caminho_arquivo)
        print(f"Historico de execução carregado: {alvo} ({chave_alvo})")
    else:
        # nao existe historico, obtendo alvos...
        print("Procurando alvos...")
        # inicializa lista_alvos
        lista_alvos = list()
        # popula lista_alvos
        encontra_alvos(lista_alvos, listas_nome_crc32_tipos)
        if valores_globais.debug:
            print("encotra_alvos_terminou:", lista_alvos)
        # verifica quantos alvos foram encontrados
        tam_lista_alvos = len(lista_alvos)
        if tam_lista_alvos == 0:
            # se não encontrou alvos ou abre arquivador e sai ou exibe erro e sai
            checa_se_abre_arquivador(caminho_arquivo)
        elif tam_lista_alvos == 1:
            # apenas um alvo foi encontrado seleciona ele nas variaveis alvo e tipo_arquivo
            alvo, chave_alvo = lista_alvos[0]
        elif tam_lista_alvos > 1:
            # existem muito alvos, tenta redusir a lista convenientemente
            # se escolha manual estiver desliagada, claro...
            if not valores_globais.manual and bool(valores_globais.config_dict["escolhe_primeiro_se_iguais"]):
                alvo, chave_alvo = resolve_conflitos_roms_validas(lista_alvos)
            if alvo == "":
                # recorre a escolha manual
                alvo, chave_alvo = escolha_manual(lista_alvos, ("Sair do programa", "Nenhum destes..."))
                # checa se escolheu sair do programa
                if chave_alvo == "Nenhum destes...":
                    exit(0)
                print("alvo selecionado:", alvo)
                print("tipo alvo:", chave_alvo)
    # se nao existir arquivo de save retorna None
    arquivo_save = carrega_savefile_se_existir(caminho_arquivo)
    # descompactador_handler ja foi adquirido assim como listas_nome_crc32
    # remove listas de tipos de arquivo e apaga objeto com as tres listas
    lista_nome_crc32 = listas_nome_crc32_tipos[:2]
    del listas_nome_crc32_tipos
    print("Liberando memoria não utilizada...")
    popula_ramdrive_e_executa_alvo(caminho_arquivo, chave_alvo, descompactador_handler, alvo,
                                   lista_nome_crc32, arquivo_save)


def resolve_conflitos_roms_validas(lista_alvos):
    # tem varios candidatos a roms validas
    # ordem de resolucao de conflitos, alvos prioritarios ja foram detectados antes:
    #  - testa se todos os alvos são do mesmo tipo, nesse caso utiliza o primeiro item da lista (mas pode levar a um
    #    resultado indesejavel caso o primeiro da lista não for o elemento desejado).
    # se ao fim nao houver um alvo retorna tupla "", "Desconecido"
    alvo = ""
    chave_retorno = "Desconhecido"
    tipo_primeiro = lista_alvos[0][1]
    contador = 0
    # varrer toda as tuplas e vai registrando quantas tem o mesmo tipo que o primeiro
    # guardando isso em contador.
    if not valores_globais.manual:
        for tupla in lista_alvos:
            # checa se a tupla tem o mesmo tipo do primeiro
            if tupla[1] == tipo_primeiro:
                contador += 1
        # Se checar todas as tuplas e não encontrar nenhum alvo prioritario então
        # checa se todos alvos são do mesmo tipo comparando contador com o tamanho total
        # se for igual entao todos sao do mesmo tipo
        if contador == len(lista_alvos):
            # se todos os tipos forem do mesmo tipo escolhe o primeiro:
            alvo, chave_retorno = lista_alvos[0]
            print("Todos os tipo são idênticos, escolhendo primeiro:", alvo)
    return alvo, chave_retorno


def coleta_lista_arquivos_comprimidos(caminho_arquivo, ext_arquivo, detecta_tipos) -> tuple[Any, Any]:
    # obtem os handlers apropiados para ext_arquivo
    # obtendo os nomes das funcoes
    descompactador_handler, listar_conteudo_handler = descompactadores[ext_arquivo]
    # obtendo os handlers a partir do nome do metodo que implementa a funcao em
    # descompactadores_utils
    descompactador_handler = getattr(descompactadores_utils, descompactador_handler)
    listar_conteudo_handler = getattr(descompactadores_utils, listar_conteudo_handler)
    # obtem a listagem de arquivos, crc32 e tipos no arquivo compactado utilizando o
    # handler obtido, a listagem de crc32 que sera utilizada quando a execução
    # terminar para determinar se houve algum arquivo alterado.
    listas_nome_crc32_tipos = listar_conteudo_handler(caminho_arquivo, detecta_tipos)
    # retorna o descompactador_handler ja que a extraçao so vai acontecer mais tarde
    # quando definirmos a partir das roms detectadas tanto pelo tipo quanto pelo nome
    # qual sera o alvo
    return descompactador_handler, listas_nome_crc32_tipos


def eh_um_alvo_prioritario(alvo):
    # como checar se um alvo eh prioritario.
    # 1 - checar se o nome do arquivo em alvo esta integralmente em config_dict["alvos_prioritarios"]
    # 2 - se nao encontrou, checa se tem extensao com ponto "."
    # em config_dict["alvos_prioritarios"]
    nome_arquivo = str(path.basename(alvo).lower())
    ext_arquivo = path.splitext(nome_arquivo)[1]
    return nome_arquivo in valores_globais.config_dict["alvos_prioritarios"] or ext_arquivo in valores_globais.config_dict["alvos_prioritarios"]

def carrega_savefile_se_existir(caminho_arquivo) -> Any:
    # localiza arquivos salvos se existirem
    saves_dir = path.join(".", "saves")
    arquivo_save = None
    if path.exists(saves_dir):
        lista_saves = list()
        for arquivo in listdir(saves_dir):
            if arquivo.startswith(path.basename(caminho_arquivo) + "_save_"):
                lista_saves.append(path.join(saves_dir, arquivo))
        if len(lista_saves) > 0:
            if bool(valores_globais.config_dict["carregar_save_auto"]):
                lista_saves = sorted(lista_saves)
                arquivo_save = lista_saves[-1]
            else:
                print("foram localizados saves para este arquivo, deseja carregar?")
                arquivo_save = escolha_manual(lista_saves, "*Nenhum")
                if arquivo_save == "Nenhum":
                    arquivo_save = None
    return arquivo_save


def extensao_combina_com_tipo_detectado(nome_arquivo, chave_arquivo):
    # pega extensões (extensoes na listas de extensoes nao incluem o "." no inicio)
    exts = valores_globais.dados_tipo[chave_arquivo]["ext"]
    # checa se a extensão do arquivo atual combina com o tipo (ignorando o "." inicial
    # retornado pelo splitext e convertendo em minusculas).
    return path.splitext(nome_arquivo)[1].lower() in exts, chave_arquivo


# popula lista_alvos com as rom encontradas e lista_index_rom_detectadas com
# os indexes em lista_alvos para os alvos detectados com detect_rom.
# Porem se um alvo prioritario for encontrado popula lista_alvos com apenas esse item e
# retorna uma lista vazia como lista_index_rom_detectadas
def encontra_alvos(lista_alvos, listas_nome_crc32_tipos):
    # utiliza a lista de nomes de arquivos gerada
    lista_nome_arquivos, _, lista_tipos_rom = listas_nome_crc32_tipos
    if valores_globais.debug:
        print("lista de nomes de arquivo:", lista_nome_arquivos)
        print("lista de tipo de rom:", lista_tipos_rom)
    # se escolha manual foi selecionada nao precisa levantar alvos prioritarios
    if not valores_globais.manual:
        # lida com alvos prioritarios de forma robusta
        lista_alvos_prioritarios = [a for a in lista_nome_arquivos if eh_um_alvo_prioritario(a)]
        # se detectou ao menos um alvo prioritario
        if len(lista_alvos_prioritarios) > 0:
            alvo_encontrado = lista_alvos_prioritarios[0]
            # lista_alvos vai ter apenas esse item
            chave_prioritario = encontra_chaves_prioritarias(alvo_encontrado)[0]
            print("Alvo prioritario encontrado (%s): %s" % (alvo_encontrado, chave_prioritario))
            lista_alvos.append((alvo_encontrado, chave_prioritario))
            if valores_globais.debug:
                print("Encerrando prematuramente encontra_alvos, lista_alvos atualizada...")
            return
    # este for tenta coletar todos os alvos possíveis em lista_alvos
    for c in range(len(lista_nome_arquivos)):
        # no modo manual no primeiro alvo aceito ja encerra
        if valores_globais.manual:
            if len(lista_alvos) == 1:
                # ja podemos encerrar
                return
        # obtem nome do arquivo
        alvo = lista_nome_arquivos[c]
        if valores_globais.debug:
            print("Inicio do for, alvo:", alvo)
        # obtemos o resultado de detect_rom para o alvo atual (primeiro item: tipo detectada)
        tipo_detect_rom = lista_tipos_rom[c][0]
        # preenche lista_alvo com alvo se ele for reconhecido ou selecionado manualmente
        reconhece_alvo_adicionando_a_lista_alvos(alvo, lista_alvos, tipo_detect_rom)
        if valores_globais.debug:
            print("chegou ao fundo do for, lista_alvo:", lista_alvos)


def reconhece_alvo_adicionando_a_lista_alvos(alvo, lista_alvos, tipo_detect_rom):
    if tipo_detect_rom != "Desconhecido" and tipo_detect_rom != "Diretorio":
        # converte tipo em chave valida
        chave_arquivo = resolve_tipo_detectado_em_chave(alvo, tipo_detect_rom, lista_alvos)
        # checa se tipo "Desconhecido" nao foi selecionado
        if chave_arquivo == "Desconhecido":
            return
        # inicializa como True
        tipo_detectado_satisfatoriamente = True
        # tipo ja foi detectado, porem verifica configuracao para ver se precisa
        # checar tambem a extensao do nome arquivo e gerar possivel erro
        if bool(valores_globais.config_dict["conferir_extensao_para_tipo_detectado"]):
            # realiza checagem extra na extensao do nome de arquivo
            tipo_detectado_satisfatoriamente, chave_arquivo \
                = extensao_combina_com_tipo_detectado(alvo, chave_arquivo)
        if tipo_detectado_satisfatoriamente:
            print("tipo detectado com detect_rom(%s):" % alvo, chave_arquivo)
            # salva alvo
            lista_alvos.append((alvo, chave_arquivo))
        else:
            # para desligar essa checagem configure conferir_extensao_para_tipo_detectado = 0
            # em conf/config.json
            if valores_globais.debug:
                print("O arquivo %s foi detectado como %s mas nao possui nenumas das extensões suportadas." %
                  (alvo, tipo_detect_rom))
                print("Ignorando o alvo %s..." %alvo)
                print("Para desligar essa checagem configure conferir_extensao_para_tipo_detectado = 0 em conf/config.json...")
            # if bool(config_dict["enter_para_fechar"]):
            #     input("Enter para sair...")
            # exit(1)
            return
    elif tipo_detect_rom == "Desconhecido":
        # detect_rom nao reconheceu o arquivo, mas pode ser porque as configuracoes do tipo nao
        # fornecem dados sobre o conteudo do arquivo. Ele ainda pode ser obtido pela extenao de
        # maneira menos precisa.
        chave_arquivo = tipo_do_nome_arquivo(alvo, lista_alvos)
        # checa se o tipo é conhecido...
        if chave_arquivo != "Desconhecido":
            print('tipo detectado com nome de arquivo(%s): %s' % (alvo, chave_arquivo))
            lista_alvos.append((alvo, chave_arquivo))


def encontra_chaves_prioritarias(nome_arquivo):
    nome_arquivo = str(path.basename(nome_arquivo)).lower()
    ext_nomearquivo = path.splitext(nome_arquivo)[1]
    chaves_contendo_nome_prioritario = [chave for chave in valores_globais.dados_tipo.keys()
                                        if nome_arquivo in valores_globais.dados_tipo[chave]['ext']]
    if valores_globais.debug:
        print("nome_arquivo:", nome_arquivo)
        print("ext_nomearquivo:", ext_nomearquivo)
        print("chaves_contendo_nome_prioritario:", chaves_contendo_nome_prioritario)
    # confere se ja encontrou a chave prioritaria para o nome de arquivo completo
    if len(chaves_contendo_nome_prioritario) == 1:
        return chaves_contendo_nome_prioritario
    elif len(chaves_contendo_nome_prioritario) > 1:
        # verifica se algum tem * na frente
        chaves_contendo_nome_prioritario_asterisco = [chave for chave in
                                                      chaves_contendo_nome_prioritario if chave.startswith("*")]
        if len(chaves_contendo_nome_prioritario_asterisco) == 1:
            return chaves_contendo_nome_prioritario_asterisco
    # se nao encontrou tenta com a extensao
    chaves_contendo_extensao_prioritario = [chave for chave in valores_globais.dados_tipo.keys()
                                        if ext_nomearquivo in valores_globais.dados_tipo[chave]['ext']]
    # confere se ja encontrou a chave prioritaria para a extensao de arquivo
    if len(chaves_contendo_extensao_prioritario) == 1:
        return chaves_contendo_extensao_prioritario
    if len(chaves_contendo_extensao_prioritario) == 0:
        print("Erro! Não foi encontrada chave para a extensão prioritaria:", nome_arquivo)
        print("Configuração deve possuir uma entrada em dados_tipo para extensão (com \".\" na frente) no item \"ext\".")
        if bool(valores_globais.config_dict["enter_para_fechar"]):
            input("Enter para sair...")
        exit(1)
    else:
        # fluxo normal... modo manual desligado...
        if not valores_globais.manual:
            # tenta utilizar a entrada com * na frente.
            chaves_com_asterico_na_frente = [f for f in chaves_contendo_extensao_prioritario if f.startswith("*")]
            if len(chaves_com_asterico_na_frente) == 1:
                return chaves_com_asterico_na_frente
            else:
                print("Erro! Foram encontradas mais de uma chave para o nome prioritario:", nome_arquivo)
                print("Configuração deve possuir apenas uma entrada em dados_tipo que liste %s em \"ext\":\n"
                      "ou no caso de varias entradas apenas uma com \"\"\" na frente."
                      %nome_arquivo, chaves_contendo_extensao_prioritario)
                if bool(valores_globais.config_dict["enter_para_fechar"]):
                    input("Enter para sair...")
                exit(1)
        else:
            # modo manual esta ligado retorna a lista de chaves
            return chaves_contendo_extensao_prioritario


def resolve_tipo_detectado_em_chave(alvo, tipo_detect_rom, lista_alvos=None):
    # substitui None de lista_alvos
    lista_alvos = [] if lista_alvos is None else lista_alvos
    # nome e extensao sao utilizado apenas se houver varias chaves sem nenhuma padrao (com "*")
    # na frente
    nome_arquivo = str(path.basename(alvo).lower())
    ext_arquivo = path.splitext(nome_arquivo)[1]
    # todas as chaves que contenham tipo_detect_rom como parte da prória chave
    chaves_contendo_tipo_detectado = [chave for chave in valores_globais.dados_tipo.keys() if tipo_detect_rom in chave]
    # checa se a lista é maior do que um item
    if len(chaves_contendo_tipo_detectado) > 1:
        # a lista tem varios itens
        # checa se podemos cortar caminho com algumas heuristicas (apenas se o modo
        # manual estiver desligado)...
        if not valores_globais.manual:
            # exitem mais de 1 opcao
            # primeiro tenta ver se ja nao foi selecionado algo similar antes...
            chave_retorno = encontra_chave_tipo_ja_selecionado("Desconhecido",
                                                               chaves_contendo_tipo_detectado, lista_alvos)
            if chave_retorno != "Desconhecido":
                return chave_retorno
            # tenta utiliza o nome do arquivo ou extensao como informacao extra para decidir
            chaves_contendo_tipo_detectado_e_nome_arquivo = [f for f in chaves_contendo_tipo_detectado
                                                             if nome_arquivo in valores_globais.dados_tipo[f]["ext"] or
                                                             ext_arquivo in valores_globais.dados_tipo[f]["ext"]]
            if len(chaves_contendo_tipo_detectado_e_nome_arquivo) == 1:
                return chaves_contendo_tipo_detectado_e_nome_arquivo[0]
            # nesse ponto é mais um chute mesmo
            # tenta reduzir a lista aos que tem "*" na frente, se so tiver um, retorna ele.
            chaves_contendo_asterisco_na_frete = [chave for chave in chaves_contendo_tipo_detectado if chave.startswith("*")]
            if len(chaves_contendo_asterisco_na_frete) == 1:
                return chaves_contendo_asterisco_na_frete[0]
            # infelizmente vamos recorrer a escolha manual
            tipo_arquivo = escolha_manual(chaves_contendo_tipo_detectado, "Desconhecido")
            return tipo_arquivo
        else:
            # modo escolha manual global foi selecionada
            tipo_arquivo = seleciona_tipos_modo_manual(alvo, chaves_contendo_tipo_detectado)
            return tipo_arquivo
    elif len(chaves_contendo_tipo_detectado) == 1:
        # a lista so tem um item
        if not valores_globais.manual:
            return chaves_contendo_tipo_detectado[0]
        else:
            return seleciona_tipos_modo_manual(alvo, chaves_contendo_tipo_detectado)
    else:
        # a lista esta vazia, sai com erro
        print("Erro! Não foi possível converter chave em tipo, bug interno...")
        print("tipo_detect_rom:", tipo_detect_rom)
        print("chaves_contendo_tipo_detectado:", chaves_contendo_tipo_detectado)
        if bool(valores_globais.config_dict["enter_para_fechar"]):
            input("Enter para sair...")
        exit(1)


def seleciona_tipos_modo_manual(alvo, chaves_contendo_tipo_detectado):
    # como passo adicional checa se alvo eh prioritario, se for adiciona as chaves
    if eh_um_alvo_prioritario(alvo):
        chaves_prioritarias = encontra_chaves_prioritarias(alvo)
        chaves_contendo_tipo_detectado.extend(chaves_prioritarias)
    chaves_contendo_tipo_detectado = sorted(chaves_contendo_tipo_detectado)
    print("Selecione o tipo para -> %s <-:" % alvo)
    if len(chaves_contendo_tipo_detectado) > 0:
        if valores_globais.debug:
            print("Tipos detectados:", chaves_contendo_tipo_detectado)
        print("Escolher entre os tipos detectados, todos os tipos ou nao adicionar este alvo?")
        lista_escolhas = ["Tipos detectados", "Todos"]
    else:
        print("Escolher entre todos os tipos ou nao adicionar este alvo?")
        lista_escolhas = ["Todos"]
    escolha = escolha_manual(lista_escolhas, "*Não adicinar este alvo...")
    if escolha == "Tipos detectados":
        print("Selecione o tipo para ->%s<-:" % alvo)
        tipo_arquivo = escolha_manual(chaves_contendo_tipo_detectado, "Desconhecido")
    elif escolha == "Todos":
        print("Selecione o tipo para ->%s<-:" % alvo)
        tipo_arquivo = escolha_manual(list(valores_globais.dados_tipo.keys()), "Desconhecido")
    else:
        tipo_arquivo = "Desconhecido"
    return tipo_arquivo


def checa_se_abre_arquivador(caminho_arquivo):
    if not valores_globais.config_dict["caminho_7zip"] == "":
        print("Não foi encontrado nenhum tipo reconhecido, iniciando arquivador padrão...")
        # se houver um arquivador configurado, abre ele para mostar o conteudo deste arquivo compactado
        caminho_arquivador = path.join(str(path.basename(valores_globais.config_dict["caminho_7zip"])), "7zFM.exe")
        # subproc_run([caminho_arquivador, caminho_arquivo], shell=False)
        run_and_get_retval_stdout([caminho_arquivador, caminho_arquivo])
        exit(0)
    else:
        # se nao encontrar uma rom válida termina
        print(
            "Não foi encontraddo nenhum tipo conhecido no arquivo compactado, abortando..."
        )
        if bool(valores_globais.config_dict["enter_para_fechar"]):
            input("Enter para sair...")
        exit(1)


# metodo main - mostra versão atual e crédito, cria readme.txt se não existir ainda, inicializa e argparser e realiza
# as checagens dos parâmetros fornecidos, checa arquivos e caminhos fornecidos são válidos, verifica se o arquivo
# args.caminho_arquivo é compactado a partir da extensão ou se é de um tipo reconhecido.
def main():
    # mostra versão atual e mostra créditos
    print(creditos_text)

    # cria readme.txt se necessario...
    if not path.exists('readme.txt'):
        print("Criando readme.txt...")
        cria_readme_txt()

    # inicializa argparser e checa arqumentos
    args = inicializa_e_checa_args()

    # checagens dos arquivos e caminhos fornecidos
    checa_caminhos_inicializacao(args)

    # extensões de arquivos comprimidos suportadas
    lista_extensoes_arcs = list(descompactadores.keys())
    # print("extensões suportadas:", lista_extensoes)

    # pergunta ao usuario sobre escolha manual
    pergunta_escolha_manual()

    # tenta destinguir a partir do nome de arquivo se é um arquivo compactado conhecido ou um arquivo descompactado e
    # confere o arquivo contra os magicbytes conhecidos e por ultimo executa o emulador configurado para o tipo
    # encontrado.

    # Obtenha a extensão
    partes_nome_arquivo = path.basename(args.caminho_arquivo).lower().split('.')

    match partes_nome_arquivo:
        # arquivos compactados com extensões compostas, tipo .tar.gz
        case [*_, str(preext), str(ext)] if "." + ".".join([preext, ext]) in lista_extensoes_arcs:
            if valores_globais.debug:
                print("extensão encontrada a partir do nome:", "." + ".".join([preext, ext]))
            fase2_checamagic_arquivo_comprimido(args.caminho_arquivo, "." + ".".join([preext, ext]), ext)
        # arquivos compactados com apenas uma extensao
        case [*_, str(ext)] if "." + ext in lista_extensoes_arcs:
            if valores_globais.debug:
                print("extensão encontrada a partir do nome:", "." + ext)
            fase2_checamagic_arquivo_comprimido(args.caminho_arquivo, "." + ext, ext)
        # arquivo não comprimido
        case [*_, str(ext)]:
            if valores_globais.debug:
                print("tratando arquivo fornecido como nao comprimido...")
            tipo_arquivo = detecta_tipo_arquivo(args.caminho_arquivo)
            # checa se o tipo é conhecido ja que tipo do nome pode retornar Desconhecido...
            if tipo_arquivo != "Desconhecido":
                # copia rom para diretorio temporario e executa pelo tipo
                popula_ramdrive_e_executa_alvo(args.caminho_arquivo, tipo_arquivo)
            else:
                # exibe mensagem informando que o arquivo é desconhecido...
                print("Arquivo sem suporte. Não existe (ainda) um programa associado com a extensão: .%s ou o conteudo."
                      %ext)


def detecta_tipo_arquivo(caminho_arquivo):
    # tenta detectar tipo usando detect_rom
    detetor = ChecaMagic("conf/roms_mb.json")
    tipo_detect_rom_resultado = detetor.detecta_tipo(caminho_arquivo)
    if tipo_detect_rom_resultado[0] != "Desconhecido":
        # converte em chave
        chave_arquivo = resolve_tipo_detectado_em_chave(caminho_arquivo, tipo_detect_rom_resultado[0])
        print("tipo do arquivo fornecido detectado com detect_rom(%s):" % caminho_arquivo, chave_arquivo)
    else:
        # detect_rom nao detectou o arquivo tenta pelo nome de arquivo
        chave_arquivo = tipo_do_nome_arquivo(caminho_arquivo)
        print("tipo detectado pelo nome de arquivo fornecido:", chave_arquivo)
    return chave_arquivo


def fase2_checamagic_arquivo_comprimido(caminho_arquivo, ext_composta, ext_final):
    print("Extensão do arquivo fornecido:", ext_composta)
    # verifica se os arquivos comprimidos são do tipo presumido
    detetor = ChecaMagic(arcs_mb_dict)
    tipo, magic_encoded = detetor.detecta_tipo(caminho_arquivo)
    print("tipo do arquivo detectado:", tipo)
    if ext_final in tipo.lower():
        # chama encontra_e_processa_alvos o pre requisito é que o dicionario de descompacatores
        # possua uma entrada para o tipo especifico contendo um metodo para extrair os arquivos
        # e um metodo para listar todos os arquivo
        fase3_encontra_e_processa_alvos(caminho_arquivo, ext_composta)
    elif tipo == "Desconhecido":
        print("Erro! Arquivo compactado corrompido ou inválido.")
        if bool(valores_globais.config_dict["enter_para_fechar"]):
            input("Enter para sair...")
        exit(1)
    else:
        print("Erro! Arquivo foi detectado como %s mas tem extensão incopativel com esse tipo." %tipo)
        if bool(valores_globais.config_dict["enter_para_fechar"]):
            input("Enter para sair...")
        exit(1)

# inicia a funcao main caso o programa seja iniciado pela linha de comando e não importado
if __name__ == '__main__':
    main()
