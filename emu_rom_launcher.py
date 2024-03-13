# changelog:
#
# v0.1f
# - nova funcionalidade: agora detecta arquivos usando os métodos em detect_rom.py que se de utiliza magic bytes
#   codificados no arquivo magic_bytes.json. É utilizado inicialmente para detectar os tipos de arquivo e caso um
#   arquivo nao possa ser detectado utiliza o nome de arquivo, extensão e por último escolha manual.
# - agora .gz, .bz2 e .xz possuem metodo de listar conteudos em descompactadores_utils configurados no dicionario de
#   descompactadores, isso foi necessario para suportar crc32 e detect_rom.
# - simplificado o bloco match em main, agora .gz, .bz2 e .xz é tratado como todos os outros arquivos compactados.
# - como efeito colateral tivemos que mudar como a extensão do arquivo é encontrada para poder pegar extensões
#   compostas. ex: .tar.gz
# - agora o dicionário de descompactadores reside em descompactadores.json e suas definições foram movidos para
#   descompactadores_dict.py para que possa ser utilizada por outros módulos do codigo..
# - config_dict não é mais global e foi movido para config_dict.py e pode ser importado em outras partes, como por
#   exemplo em descompactadores_utils.py.
# - alterado como arquivos .tar.gz, .tar.bz2 e .tar.xz listam seus conteudos antes utilizava o metodo do .tar com opcao
#   modo setado para tipo, funciona mas tem pessima performance ao fazer operações em arquivo um por um. Agora criamos
#   um .tar em um diretorio temporario utilizando o metodo já disponível de extrair arquivos do tipo em questão e após
#   é utilizado o método do .tar para listar diretamente o arquivo temporário previamente criado. A performance obtida
#   justifica o código extra já que antes o gerenciador de contexto perdia muito tempo descomprimindo os mesmos streams
#   de bytes diversas vezes para acessar cada arquivo dentro do tar, agora a descompressão é feita no arquivo inteiro só
#   uma única vez.
# - simplificado ainda mais o bloco match em main, agora todas as extensões dos arquivos são comparadas a partir de uma
#   lista de extensões criada das chaves do dicionario de descompactadores. O que centralizou em descompactadores.json
#   todas as configurações para adicionar um formato de arquivo compactado novo.
# - movido dados_tipo para dados_tipo_dict.py
# - refatorado metodo processa_arquivo, se parametro alvo for vazio faz ele ser o basename de caminho_arquivo o que
#   simplificou o codigo que seta o destino.
# - converte_tipo_em_chave: adicionado escolha manual se apertar algum tecla na inicializacao.
# - escolha_manual: workarround bug que impede uma lista com mais de 10 itens ser selecionado, pois so le uma tecla.
#   A lista pode ter no maximo 36 itens entao so mostra os primeiros 36. Os caracteres validos sao de 0 a 9 e A a Z.
# - novo metodo em json_config.py carrega_config que so carrega o json sem se preocupar em criar.
# - detect_rom agora exporta a classe DetectaMagicBytes e permite configurar um json especifico.
# - arquivos compactados tem seu tipos checados e comparados com a extensão atual pra evitar abrir arquivos inválidos.
# - reverte para deteccao com nome de arquivo caso o detect_rom detecte um tipo cuja a extensão não condiza com o
#   nome do arquivo (e que se por sua vez nao for possivel detectar retorna Desconhecido).
# - ajustado arquivo "arquivos_compactados.json" para os arquivos do tipo lha retornarem "LHA LZH" ao invez de apenas
#   "LHA".
# - alterado comparação em main para que a extensão esteja contida na string retornada como tipo pelo detector de magic
#   bytes dos arquivos compactados (corrigindo o caso do .lzh que havia parado de funcionar com a adição da checagem por
#   magic bytes).
# - adicionado suporte a saves, ao carregar jogos do dosbox ou que extraiam todos os arquivos do arquivo compactado,
#   coleta todos os arquivos alterados e criados e salva em um arquivo compactado criado no diretorio ./saves com o nome
#   original do arquivo mais "_save_XXX.tar.xz" onde XXX é um número que inicia em 000 e vai incrementado caso já esteja
#   utilizado.
# - ao iniciar arquivo do dosbox ou que extraiam tudo é checado se existem arquivo salvos anteriormente no diretorio
#   ./saves com o nome original mais "_save_XXX.tar.xz" onde XXX é um número que inicia em 000 e vai incrementando e se
#   forem encontradas exibe uma lista de escolha manual para escolher qual save deve ser extraido ou se inicia sem.
# - suporte ao pma adicionado via lha.exe (v 0.3).
# - suporta a .arj adicionado via unarj.exe modificado por mim mesmo!
# - suporta o caractere de comando ?a para substituir pelo nome do alvo selecionado no arquivo compactado na composição
#   da linha de comando para o tipo em questão.
# - agora o todos os argumentos são checados por caracteres de comando de substituição e não para no primeiro
#   encontrado assim substituindos em todos os argumentos.
# - revertido para lha.exe para o suporte a .lha e .lzh.
# - Changelog sera descontinuado, agora o codigo vai ser mantido por git! :)
#
# v0.1e
# - adicionado changelog :) e corrigindo bug que impede a abertura de .bz2 .gz e agora tambem .xz que agora é suportado,
#   o bug em questao tem haver com determinar o tipo do arquivo baseado na extensao compacatada ao inves do alvo e foi
#   introduzido nao sei quando uma vez que o suporte a gz e bz2 ja funcionaram no passado, melhorar o teste e isso que
#   motivou o changelog...
# - adicionado suporte a arquivos .tar sem compressão e arquivos .tar.xz e .xz
# - adicionado suporte adicional multiplataforma (apenas win32 no momento o que cobre x64 tambem)
# - restruturação do codigo movendo todos as funcoes especificas do windows para emu_rom_launcher_win32
# - restruturação do codigo movendo todos os descompactadores para descompactadores_utils
# - restruturação do codigo movendo todos os textos e strings para emu_rom_launcher_textos
# - implementado auto resolução de conflitos quando um tipo de arquivo detectado ja existe como alvo, e quando todos os
#   alvos são do mesmo tipo, utilizando o primeiro alvo.
# - e varias outras pequenas correções e restruturações.
# - adicionado checagem de error de execução ao listar ou descompactar aqruivos, terminando o programa e exibindo a
#   o arquivo corrompido e detalhes do erro.
# - corrigido bug no codigo que adiciona o nome do arquivo e caminho completo como ultimo parametro quando nenhum
#   caractere especial é encontrado, o bug era que o parametro era adiciona uma vez para cada argumento que nao houvesse
#   caractere especiais, o certo é apenas uma vez ao final.
# - adicinado um input para reter o fechamento da janela para que o usuario possa ler as mensagens de erros na saida.
# - adicionado parâmetro "usa_arquivador" em config.json que permiter configurar um arquivador padrão para abrir o
#   arquivo compactado caso não encontre nenhum tipo conhecido.
# - removido usa da funcao copyfileobj, substituido por um saida.write(entrada.read()) :)
# - adicionado checagens que faltavam de tipo para evitar processar arquivod de tipo desconhecido quando especificado,
#   diretamente na linha de comando ou em arquivos .gz, .bz2 e .xz.
# - adicionando suporte a especificar um nome de arquivo com extensão ao invés de apenas a extensão para permitir
#   detectar de maneira mais avançada tipos como disco de boot de msxdos (msxdos.sys)
# - adicionado documentação de como criar jogos compactados para o Dosbox.
# - removido a necessidade de um arquivo DOSGAME.OLD agora apenas o arquivo com nome "arquivo_bat_dosbox" definido em
#   config.json é necessário.
# - adicionado lista_nao_aplicavel para que o programa memorize quais os tipo nao sao relevantes naquele caso e nao
#   exiba mais essas escolhas
# - ajustes no codigo de tipo_do_nome_arquivo e escolha_manual para que a lista_nao_aplicavel funciona corretamente
# - escolha_manual agora exibe uma opção nao aplicavel definida pelo objeto chamador
# - exibe a opção de sair do programa sem executar nada se houver mais de um alvo (utilizando a escolha nao aplicavel
#   recem adicionada).
# - agora um nome de dado pode conter um * como primeiro caractere e isso sinaliza que ele é o padrão se houverem outros
# - nome de arquivo bat padrao do dosbox mudou de "DOSSTART.BAT" para a string configurada em "arquivo_bat_dosbox"
#   do arquivo config.json
# - agora os menus podem ter um timeout configurado por "tempo_espera_escolha" no arquivo config.json quando existir um
#   comando padrão para este tipo.
# - corrigido e atualizado textos para refletir últimas mudanças como parametro novos do arquivo config.json
#   "arquivo_bat_dosbox" e "tempo_espera_escolha".
# - agora é possível digitar enter numa escolha manual e selecionar a escolha padrão.
# - refatorado o codigo de inicializacao em inicializa_e_checa_args() e checa_caminhos_inicializacao(args)
# - refatorado processa_arquivo_compactado() em processa_arquivo() permitindo que o metodo seja utilizado
#   quando especificado um arquivo rom diretamente, bastando passar None como descompactador e "" como alvo.
# - implementado verificação dos arquivo com crc32 para checar por arquivos alterados durante a execução.
# - implementado verificação de arquivos novos criados durante a execução.
# - adaptado todos os decompressores para listar os arquivos e exportas duas listas uma de arquivos que tenham um crc32
#   valido e tenham / como separador de diretorios e outra com o crc32 de cada arquivo.
# - adicionado suporte a .lha (so faltava configurar a extensao no dicionario de descompactadores e na clausula case
#   em main).
# - adicionado chave "alvos_prioritarios" em config.json para flexibilizar as regras de resolução de conflitos para os
#   tipos de alvos diferentes adicionados posteriormente.
# - removido chave "arquivo_bat_dosbox" de config.json pois ela foi substituida pela mais flexivel opção
#   "alvos_prioritarios".

from argparse import ArgumentParser, RawTextHelpFormatter
from tempfile import TemporaryDirectory
from sys import platform as sys_platform
from os import walk, listdir, mkdir
# descompactadores o import tem que ser o tradicional para usar getattr
import descompactadores_utils
# importa todas as strings
from emu_rom_launcher_textos import *
# importa calcular_crc32
from crc32_utils import calcular_crc32_arquivo
# importar detect_rom
from detect_rom import DetectMagicBytes
# importar dicionario de config
from config_dict import config_dict
# importar dicionario de descompactadores
from descompactadores_dict import descompactadores
# importar dicionario de dados
from dados_tipo_dict import dados_tipo

# encontra a plataforma atual
PLATAFORMA = sys_platform

# modo debug
modo_debug = True

# variavel que define o uso prioritario da escolha manual
manual = False

# realiza imports adicionais especificos da plataforma
if PLATAFORMA == 'win32':
    # import especifico do windows
    print("Plataforma Windows detectada...")
    from emu_rom_launcher_win32 import *

# lista de chaves que não são aplicáveis selecionadas pelo usuario
lista_nao_aplicavel = list()


# implementação inicial do metodo que le apenas uma tecla, no momento apenas windows, se for linux ou outro usa input.
def le_tecla():
    if PLATAFORMA == 'win32':
        tecla = le_tecla_win32()
    else:
        print("Digite a opção e enter para confirmar: ", end="")
        tecla = input()
    return tecla


def tecla_foi_pressionada():
    if PLATAFORMA == 'win32':
        return tecla_foi_pressionada_win32()
    else:
        print("Erro - Ainda não possui implementação para tecla_foi_pressionada."
              "Plataforma %s ainda não suportada..." % PLATAFORMA)
        exit(1)


# exibe a lista de escolhas mostra um input perguntando a escolha correta
def escolha_manual(lista_escolhas, escolha_nao_aplicavel):
    # adiciona opcao escolha_nao_aplicavel ao fim da lista
    lista_escolhas.append(escolha_nao_aplicavel)
    # cria copia da lista escolhas para poder alterar os nomes
    lista_exibicao = lista_escolhas[:]
    # carrega valor timeout
    timeout = config_dict["tempo_espera_escolha"]
    # index da escolha padrão, -1 nao tem escolha padrao
    escolha_padrao = -1
    tamanho_lista_escolhas = len(lista_escolhas)
    # workarround lista so com um caractere
    if tamanho_lista_escolhas > 36:
        # lista muito grande
        print('A quantidade de escolhas é maior que 36, mostrando apenas as primeiras 36...')
        tamanho_lista_escolhas = 36
    letras = [chr(ord('a') + i) for i in range(26)]
    itens = [f"Item {i}" if i < 10 else f"Item {letras[i - 10]}" for i in range(tamanho_lista_escolhas)]
    # mostra opções na tela
    print("Existem %d escolhas possiveis:" % tamanho_lista_escolhas)
    for c in range(tamanho_lista_escolhas):
        # se alguma das alternativas é str e começa com * é escolha padrão, guarda este valor
        if type(lista_escolhas[c]) == str and lista_escolhas[c][0] == "*":
            # remove * do nome em lista_nomes
            lista_exibicao[c] = lista_exibicao[c][1:]
            escolha_padrao = c
        # se for tupla e o segundo valor comecar com um * é a escolha padrão, guarda este valor
        elif type(lista_escolhas[c]) == tuple and lista_escolhas[c][1][0] == "*":
            # remove * do segundo item em lista_nomes
            lista_exibicao[c] = (lista_exibicao[c][0], lista_exibicao[c][1][1:])
            # sem escolha padrao para este tipo
            # escolha_padrao = c
        # mostra opção na tela
        if c == escolha_padrao:
            print("%s - %s <- escolha padrão" % (itens[c], lista_exibicao[c]))
        else:
            print("%s - %s" % (itens[c], lista_exibicao[c]))
    print("Qual opção você escolhe?")
    # prepara o loop e espera uma escolha valida
    escolha_index = -1
    inicio = time()
    # enquanto escolha_index nao estiver entre 0 e tamanho_listas_escolhas - 1 ou seja nao estiver sido selecionado.
    while not 0 <= escolha_index <= tamanho_lista_escolhas - 1:
        # inicia contagem de tempo se existir uma escolha padrão
        if escolha_padrao != -1:
            tempo_decorrido = time() - inicio
            escreve_contador_regressivo(tempo_decorrido, timeout)
            # checa se o tempo do timeout ja passou
            if tempo_decorrido > timeout:
                # acabou o tempo para escolher outra opção, executa usando a opção padrão
                escolha_index = escolha_padrao
                print("\nTimeout, escolhendo o padrão...", end="")
        # se alguma tecla foi pressionada le o valor
        if tecla_foi_pressionada():
            if escolha_padrao != -1:
                print("")
            tecla_digitada = le_tecla()
            # checa se é um digito numerico valido e seta escolha_index corretamente
            if tecla_digitada.isdigit() and 0 <= int(tecla_digitada) <= tamanho_lista_escolhas - 1:
                escolha_index = int(tecla_digitada)
                print("Escolhendo opção", lista_exibicao[escolha_index], end="")
            # checa se a opcao é uma letra e esta dentro das opcoes validas
            elif tecla_digitada.isalpha() and 0 <= ord(tecla_digitada) - 87 <= tamanho_lista_escolhas - 1:
                escolha_index = ord(tecla_digitada) - 87
                print("Escolhendo opção", lista_exibicao[escolha_index], end="")
            # checa se foi digitado "enter" e se há uma escolha padrão e nesse caso seleciona a escolha padrão
            elif ord(tecla_digitada) == 13 and escolha_padrao != -1:
                escolha_index = escolha_padrao
                print("Escolhendo o padrão...", end="")
            else:
                # qualquer outra coisa é tecla invalida
                print("tecla invalida...", end="")
                # se tiver em contagem adiciona um \n
                if escolha_padrao != -1:
                    print("")

    # ja temos uma escolha selecionada em escolha_index...
    # adiciona quebra de linha para que o proximo print nao utilize a mesma linha ja que o sys.stdout nao adiciona \n
    # automaticamente
    print("")
    return lista_escolhas[escolha_index]


def escreve_contador_regressivo(tempo_decorrido, timeout):
    sys_stdout.write('\rTempo restante: %d ' % int(timeout - tempo_decorrido))
    sys_stdout.flush()


# determina o tipo de arquivo a partir da extensão fornecida e dentro dos tipos configurados
def tipo_do_nome_arquivo(caminho_arquivo, lista_encontrados=None):
    global lista_nao_aplicavel
    # extrai o nome de arquivo do caminho completo fornecido
    nome_arquivo = path.basename(caminho_arquivo)
    # cria uma nova lista a partir do valor fornecido inicialmente, se for uma lista permanece identica se for None cria
    # uma lista vazia.
    lista_encontrados = list(lista_encontrados or [])
    # lista de chaves encontradas
    lista_chaves = list()
    for chave in dados_tipo.keys():
        # checa se chave nao esta na lista nao aplicavel a este arquivo
        if chave not in lista_nao_aplicavel:
            # checa se o nome de arquivo ou se a extensão dele existe na lista em 'ext' em minusculas
            if (nome_arquivo.lower() in dados_tipo[chave]['ext'] or
                    path.splitext(nome_arquivo)[1][1:].lower() in dados_tipo[chave]['ext']):
                # adiciona chave a lista de chaves possiveis
                # print("Encontrado possivel tipo (%s) para o arquivo: %s" % (chave, caminho_arquivo))
                lista_chaves.append(chave)
    # valor do tipo a ser retornado
    tipo_retorno = "Desconhecido"
    # if len(lista_chaves) == 0:
    #     return "Desconhecido"
    # se ja tiver encontrado um alvo prioritario não precisa procurar mais retorna desconhecido e continua...
    if not any(nome.lower() in config_dict["alvos_prioritarios"] for nome, _ in lista_encontrados):
        if len(lista_chaves) == 1:
            # se nao tiver encontrado alvo prioritario retorna elemento encontrado
            tipo_retorno = lista_chaves[0]
        elif len(lista_chaves) > 1:
            # ha muitos candidatos a chaves corretas
            # se ja exite alguma das escolhas possiveis entre os items em lista_encontrados, assume este como correto
            # tambem para o arquivo atual.
            for chave in lista_chaves:
                # checa se ja existe uma das escolhas como segundo item de alguma tupla em lista_encontrados
                if any(tipo == chave for _, tipo in lista_encontrados):
                    # se tiver a chance é muito alta desse ser a escolha correta
                    # print("item escolhido por ter sido encontrado anteriormente:", chave)
                    tipo_retorno = chave
            if tipo_retorno == "Desconhecido":
                # recorrendo a escolha manual...
                print("Determine o tipo de %s:" % caminho_arquivo)
                escolha = escolha_manual(lista_chaves, "Nenhum destes.")
                # checa se escolha e a opcao não aplicavel
                if escolha == "Nenhum destes.":
                    # se for adiciona lista_chaves a lista_nao_aplicavel e retorna "Desconhecido"
                    lista_nao_aplicavel += lista_chaves
                    # return "Desconhecido"
                else:
                    tipo_retorno = escolha
    return tipo_retorno


# funcao que executa o comando personalizado em "cmd", inicialmente checa se o valor de "dos" é verdadeiro se for
# modifica caminho_arquivo para que o nome e diretorio do arquivo nao ultrapasse 8 caracteres emulando o estilo do
# win95 adicionando ~1 no fim do nome. Em seguida checa todos os argumentos em "cmd" pelos caracteres especiais
# "?c", "?d", "?D" e "?a" significando o nome do arquivo com caminho completo, caminho do diretorio relativo ao
# diretorio temporário, caminho do diretório completo temporário e nome do alvo encontrado, se não houver caracteres
# especiais o caminho completo mais nome do arquivo rom é adicionado como último parâmetro de "cmd".
def executar_comando_para_tipo_arquivo(tipo_arquivo, caminho_arquivo, alvo=""):
    dos = dados_tipo[tipo_arquivo]['dos']
    print("Nomes de arquivos compatível com DOS:", dos)
    # se dos estiver setado ajusta tamanho do diretorio e do nome do arquivo
    if dos:
        print("Truncando nomes para DOS...")
        tam = len(config_dict["caminho_temp_dir"])
        temp_nome, temp_ext = path.splitext(path.basename(caminho_arquivo))
        if len(temp_nome) > 8:
            temp_nome = temp_nome[:6] + "~1"
        caminho_arquivo = path.join(caminho_arquivo[:tam + 6] + "~1", temp_nome + temp_ext)
    print("Configurando comando para:", tipo_arquivo)
    argumentos = dados_tipo[tipo_arquivo]['cmd']
    # marcadores válidos:
    # ?a - alvo
    # ?d - diretorio temporário relativo
    # ?D - diretorio temporário completo
    # ?c - caminho completo com nome de arquivo
    print("Procurando marcadores nos argumentos... (" + str(len(argumentos)) + " argumentos)")
    # esta for passa por todos os argumentos do ultimo ate o primeiro
    adicionado_ok = False
    for indice_param in range(len(argumentos) - 1, -1, -1):
        # procura por ? na string
        indice_marcador = argumentos[indice_param].find('?')
        while indice_marcador > -1:
            # parametro possui ao menos um ? entao verifica proximo caractere:
            match argumentos[indice_param][indice_marcador + 1]:
                case "a":
                    # substitui por alvo
                    print("Injetando " + alvo + " no parametro " + str(indice_param - 1) + "...")
                    argumentos[indice_param] = argumentos[indice_param].replace('?a', alvo)
                    # procura novamente
                    indice_marcador = argumentos[indice_param].find('?')
                case "c":
                    # substitui por caminho_arquivo
                    print("Injetando " + caminho_arquivo + " no parametro " + str(indice_param - 1) + "...")
                    argumentos[indice_param] = argumentos[indice_param].replace('?c', caminho_arquivo)
                    # procura novamente
                    indice_marcador = argumentos[indice_param].find('?')
                    # terminamos com o loop
                    # break
                    adicionado_ok = True
                case "d":
                    # substitui por diretorio sem drive e sem o nome de arquivo
                    diretorio_relativo = path.splitdrive(path.dirname(caminho_arquivo))[1]
                    print("Injetando " + diretorio_relativo + " no parametro " +
                          str(indice_param - 1) + "...")
                    argumentos[indice_param] = argumentos[indice_param].replace('?d', diretorio_relativo)
                    # procura novamente
                    indice_marcador = argumentos[indice_param].find('?')
                    # terminamos com o loop
                    # break
                    adicionado_ok = True
                case "D":
                    # substitui por diretorio com drive e sem o nome de arquivo
                    diretorio_relativo = path.dirname(caminho_arquivo)
                    print("Injetando " + diretorio_relativo + " no parametro " +
                          str(indice_param - 1) + "...")
                    argumentos[indice_param] = argumentos[indice_param].replace('?D', diretorio_relativo)
                    # procura novamente
                    indice_marcador = argumentos[indice_param].find('?')
                    # terminamos com o loop
                    adicionado_ok = True
                case _:
                    # comando mal formado:
                    print("Erro: Argumento mal formado. %s - (posição: %d)" %
                          (argumentos[indice_param], indice_marcador + 1))
                    exit(1)
    # checa se ja adicionou o caminho ou diretorio nos parametros
    if not adicionado_ok:
        # como nao encontrou os caractere especiais nos parametros adiciona caminho_arquivo como ultimo parametro
        print('Adicinando', caminho_arquivo, "como último parametro.")
        argumentos.append(caminho_arquivo)
    # Executa o comando
    print("comando:", " ".join(argumentos))
    subproc_run(" ".join(argumentos), shell=False)


# Método copia a rom a ser executada para um diretorio temporario com um nome definido por "arquivo_rom" em config.json
# ou uma versao do nome do arquivo original substituindo os espaços por "_" e executa o comando associado com o
# tipo_arquivo. Opcionalmente checa se algum arquivo foi adicionado ou alterado e salva essa lista de arquivo no caso
# de haver algum no diretorio ./saves com o nome original do arquivo mais "_save_XXX.tar.xz" onde XXX é um número que
# inicia em 000 e vai incrementado caso já esteja utilizado..
# Se descompactador for None nao extrai arquivos e parâmetro alvo nao precisa ser especificado podendo apenas ter valor
# "" e apos copia caminho_arquivo para o diretorio temporário utilizando o nome previamente definido.
# Se descompactador for especificado verifica o valor de "extrai_tudo".
# Se falso utiliza o alvo e o tipo de arquivo ja definidos anteriormente e descompacta o alvo no diretorio temporario
# criando um arquivo com nome definido anteriormente.
# Se o valor de "extrai_tudo" for verdadeiro extrai todos arquivos do arquivo compactado no diretorio temporario.
# Chama executar_comando_para_tipo_arquivo() para que o comando personalizado para o tipo_arquivo seja
# executado para o arquivo em destino.
# Por fim se tiver extraido tudo verifica por arquivo novos ou alterados no ramdrive e salva eles em ./saves caso
# existam.
def processa_arquivo(caminho_arquivo, tipo_arquivo, descompactador=None, alvo="", listas_nome_crc32=None,
                     arquivo_salvo=None):
    # se nao foi especificado faz alvo ser o nome (basename) de caminho_arquivo
    if alvo == "":
        alvo = path.basename(caminho_arquivo)
    # variável destino guarda valor do caminho no diretorio temporario mais nome do arquivo a ser escrito, porém quando
    # todos os arquivos existentes no arquivo compactado serão extraídos utiliza apenas o dirname de destino (o caminho
    # no diretorio temporario)
    # Cria um diretório temporário no RAM drive
    with (TemporaryDirectory(dir=config_dict["caminho_temp_dir"]) as temp_dir):
        # variavel que define se todos os arquivos serão descompactados ou apenas o alvo fornecido.
        extrai_tudo = dados_tipo[tipo_arquivo]["extrai_tudo"]
        # seta o destino
        if config_dict["arquivo_rom"] != "":
            # se "arquivo_rom" nao for "" utiliza o nome padrão com extensão original em minusculas
            ext = path.splitext(alvo)[1].lower()
            destino = path.join(temp_dir, config_dict["arquivo_rom"] + ext)
        else:
            # destino tera o nome em caminho_arquivo em minusculas e sem espacos
            nome_alterado = alvo.lower().replace(" ", "_")
            destino = path.join(temp_dir, nome_alterado)
        # checa se é necessário descompactar o arquivo antes
        if descompactador is None:
            # não é necessário, arquivo rom foi especificado diretamente
            # copia arquivo para diretorio temporario
            with open(caminho_arquivo, 'rb') as entrada, open(destino, 'wb') as saida:
                saida.write(entrada.read())
                print("rom copiada para:", destino)
        else:
            # foi especificado um arquivo compactado...
            # checa se extrairemos apenas o alvo ou se extrairemos tudo
            if not extrai_tudo:
                # extrai alvo no ram_drive
                descompactador(caminho_arquivo, destino, alvo)
                print(f"Arquivo extraído em: {destino}")
            else:
                # sobreescreve valor em destino
                # adiciona "\" ou "/" ao fim do diretorio dependendo do padrao do os...
                destino = path.join(temp_dir, "")
                # extrai todos arquivos no ram_drive em temp_dir
                descompactador(caminho_arquivo, destino, "")
                print(f"extraindo todos os aqruivos em: {destino}")
        # checa se carrega algum arquivo salvo
        if extrai_tudo and arquivo_salvo is not None:
            print("extraindo arquivo salvo %s em %s..." % (arquivo_salvo, temp_dir))
            descompactadores_utils.descompactar_tar_xz(arquivo_salvo, path.join(temp_dir, ""), "")
        # executa o comando correspondente ao tipo de arquivo
        executar_comando_para_tipo_arquivo(tipo_arquivo, destino, alvo)
        # se listas_nome_tamannho nao for None e tiver extraido tudo
        # checa se algum arquivo foi adicionado ou alterado
        if extrai_tudo and listas_nome_crc32 is not None:
            lista_arquivos_para_guardar = checa_arquivo_adicionado_ou_alterado(listas_nome_crc32, temp_dir)
            if len(lista_arquivos_para_guardar) > 0:
                print("lista de arquivos novos e alterados:", lista_arquivos_para_guardar)
                # criar um arquivo compactado com as alterações
                saves_dir = path.join(".", "saves")
                # cria diretorio para guardar os saves
                if not path.exists(saves_dir):
                    print("criando %s..." % saves_dir)
                    mkdir(saves_dir)
                if arquivo_salvo is None:
                    # procura um nome de arquivo novo
                    contador = 0
                    while True:
                        nome_arquivo = path.join(saves_dir, path.basename(caminho_arquivo) + "_save_%.3d.tar.xz"
                                                 % contador)
                        if not path.exists(nome_arquivo):
                            break
                        contador += 1
                else:
                    nome_arquivo = arquivo_salvo
                print("salvando alterações para o arquivo:", nome_arquivo)
                # cria arquivo compactado de nome nome_arquivo em saves_dir
                descompactadores_utils.criar_tar_xz(nome_arquivo, lista_arquivos_para_guardar, temp_dir)
        print("Aguarde enquanto o diretório temporário é removido...")


# metodo que checa se algum arquivo foi criado ou alterado e retorna uma lista desses arquivos.
def checa_arquivo_adicionado_ou_alterado(listas_nome_crc32, temp_dir):
    # cria um set a partir da lista de nomes em lista_nomes_crc32[0]
    arquivos_no_zip = set(listas_nome_crc32[0])
    # print("arquivos_no_zip:", arquivos_no_zip)
    # coleta todos nomes dos arquivos no temp_dir mas reformata os caminhos para serem relativos e usarem / como
    # separador
    # print("coletando todos nomes dos arquivos em %s..." % temp_dir)
    arquivos_no_diretorio = []
    for pasta_raiz, subpastas, arquivos_na_pasta in walk(temp_dir):
        for nome_arquivo in arquivos_na_pasta:
            caminho_completo = path.join(pasta_raiz, nome_arquivo)
            # nas lista em listas_nome_crc32[0] os caminhos são relativos
            caminho_relativo = path.relpath(caminho_completo, temp_dir)
            if PLATAFORMA == "win32":
                # reformata a string para usar / como separador de diretorios
                caminho_relativo = caminho_relativo.replace("\\", "/")
            arquivos_no_diretorio.append(caminho_relativo)
    # cria o set a partir da lista encontrada
    arquivos_no_diretorio = set(arquivos_no_diretorio)
    # print("arquivos_no_diretorio:", arquivos_no_diretorio)
    # Arquivos novos é calculado subtraindo o set em arquivos_no_zip do set arquivos_no_diretorio, guarda resultado
    # como uma lista
    arquivos_novos = list(arquivos_no_diretorio - arquivos_no_zip)
    # print("arquivos_novos:", arquivos_novos)
    # Arquivos alterados é uma lista criada a partir da interseção de arquivos_no_diretorio e arquivos_no_zip onde cada
    # elemento foi adicionado porque seu crc32 atual nao bateu com o crc32 calculado antes da execução.
    # print("listas_nome_crc32:", listas_nome_crc32)
    arquivos_alterados = [arquivo for arquivo in arquivos_no_zip.intersection(arquivos_no_diretorio)
                          if calcular_crc32_arquivo(path.join(temp_dir, arquivo)) !=
                          listas_nome_crc32[1][listas_nome_crc32[0].index(arquivo)]]
    # print("arquivos_alterados:", arquivos_alterados)
    # tudo foi convertido em listas pois sets so podem ser subtraido e nao somados.
    return arquivos_novos + arquivos_alterados


# metodo que auxilia a encotrar possiveis alvos no arquivo compactado, se a lista de alvos for maior que 1 tenta
# definir o alvo correto por heuristica ou escolha manual caso não seja possivel diretamente, se for 0 sai do
# programa. O tipo de arquivo precisa existir no dicionario de descompactadores com uma função para extrair deste tipo
# de arquivo compactado e uma função que possa listar os conteúdos do arquivo compactado
def encontra_e_processa_alvos(ext_arquivo, caminho_arquivo):
    global manual
    # inicializa diversas variáveis
    # valor inicial tipo_arquivo
    tipo_arquivo = "Desconhecido"
    # lista para os alvos encontrados
    lista_alvos = list()
    alvo = ""
    # obtem os handlers apropiados para ext_arquivo
    descompactador, listar_conteudo_handler = descompactadores[ext_arquivo]
    descompactador = getattr(descompactadores_utils, descompactador)
    listar_conteudo_handler = getattr(descompactadores_utils, listar_conteudo_handler)
    # obtem a listagem de arquivos no arquivo compactado e a listagem de crc32 que sera utilizada quando a execução
    # terminar para determinar se houve algum arquivo alterado.
    listas_nome_crc32_tipos = listar_conteudo_handler(caminho_arquivo)
    # utiliza a lista de nomes de arquivos gerada
    lista_nome_arquivos, _, lista_tipos_rom = listas_nome_crc32_tipos
    if modo_debug:
        print("lista de nomes de arquivo:", lista_nome_arquivos)
        print("lista de tipo de rom:", lista_tipos_rom)
    # este for tenta coletar todos os alvos possíveis em lista_alvos
    lista_index_rom_detectadas_com_detect_rom = list()
    for c in range(len(lista_nome_arquivos)):
        # obtem nome do arquivo
        nome_arquivo = lista_nome_arquivos[c]
        # verificamos primeiro o resultado de detect_rom
        tipo_detect_rom = lista_tipos_rom[c]
        if tipo_detect_rom[0] != "Desconhecido":
            # tipo foi detectado por detect_rom converte tipo para chave em dados_tipos
            # print("detect_rom retornou:", tipo_detect_rom)
            # converte tipo em chave valida
            tipo_arquivo = converte_tipo_em_chave(tipo_detect_rom[0])
            # pega extensões
            exts = dados_tipo[tipo_arquivo]["ext"]
            # checa se a extensão do arquivo atual combina com o tipo
            if path.splitext(nome_arquivo)[1][1:].lower() in exts:
                print("tipo detectado com detect_rom(%s):" % nome_arquivo, tipo_arquivo)
                # salva index na lista para ser utilizado na etapa de resolução de conflitos se for o caso
                lista_index_rom_detectadas_com_detect_rom.append(len(lista_alvos))
                # salva alvo
                lista_alvos.append((nome_arquivo, tipo_arquivo))
            else:
                # Verificação se o tipo de arquivo é conhecido
                tipo_arquivo = tipo_do_nome_arquivo(nome_arquivo, lista_alvos)
                # checa se o tipo é conhecido...
                if tipo_arquivo != "Desconhecido":
                    print('tipo detectado com nome de arquivo: %s' % tipo_arquivo)
                    lista_alvos.append((nome_arquivo, tipo_arquivo))
        else:
            # detect_rom nao reconheceu o arquivo entao verifica o tipo de arquivo por nome
            # Verificação se o tipo de arquivo é conhecido
            tipo_arquivo = tipo_do_nome_arquivo(nome_arquivo, lista_alvos)
            # checa se o tipo é conhecido...
            if tipo_arquivo != "Desconhecido":
                print('tipo detectado com nome de arquivo: %s' % tipo_arquivo)
                lista_alvos.append((nome_arquivo, tipo_arquivo))
    # verifica quantos alvos foram encontrados
    tam_lista_alvos = len(lista_alvos)
    if tam_lista_alvos == 0:
        # se não encontrou alvos ou abre arquivador e sai ou exibe erro e sai
        checa_se_abre_arquivador(caminho_arquivo)
    elif tam_lista_alvos == 1:
        # apenas um alvo foi encontrado seleciona ele nas variaveis alvo e tipo_arquivo
        alvo, tipo_arquivo = lista_alvos[0]
    elif tam_lista_alvos > 1:
        # tem varios candidatos a roms validas
        # ordem de resolucao de conflitos:
        # primeiro testa se manual esta em True o que significa que a escolha manual é prioridade, pulando todas as
        # seguintes:
        #  - testa por alvos prioritários listados em "alvos_prioritarios" do config.json.
        #  - testa se todos os alvos são do mesmo tipo, nesse caso utiliza o primeiro item da lista (mas pode levar a um
        #    resultado indesejavel caso o primeiro da lista não for o elemento desejado).
        #  - testa foi encontrada apenas um alvo utilizando o detect_rom checando se o tamanho das listas de index
        #    encontradas com detect_rom é um, nesse caso escolhe esse alvo pelo index salvo.
        # se ao fim nao houver um alvo realiza a escolha manual.
        # setando valor inicial das variaveis de controle
        alvo = ""
        tipo_primeiro = lista_alvos[0][1]
        contador = 0
        # lista de alvos que tem mais prioridade para ajudar na resolução de conflitos
        alvos_com_prioridade = config_dict["alvos_prioritarios"]
        # esse for tem duas funcoes:
        # primeiro procura pelo alvo prioritario no primeiro item da tupla (quebrado o loop) e
        # segundo ao varrer todas as tuplas vai registrando quantas tem o mesmo tipo que o primeiro guardando isso em
        # contador.
        if not manual:
            for alvo_prioridade in alvos_com_prioridade:
                for tupla in lista_alvos:
                    # checa se a tupla tem alvo prioritario
                    if alvo_prioridade in tupla[0].lower():
                        # se tiver seta alvo e tipo_arquivo
                        alvo, tipo_arquivo = tupla
                        print('lista_alvos coletada:')
                        for item in lista_alvos:
                            print(item)
                        print("Encontrado alvo prioritário %s, escolhendo tipo: %s" % (alvo_prioridade, tipo_arquivo))
                        break
                    # checa se a tupla tem o mesmo tipo do primeiro
                    elif tupla[1] == tipo_primeiro:
                        contador += 1
                # checa se ja foi determinado alvo para terminar o loop
                if alvo != "":
                    break
            # Se checar todas as tuplas e não encontrar nenhum alvo prioritario então checa se todos alvos são do mesmo
            # tipo comparando contador com o tamanho total se for igual entao todos sao do mesmo tipo
            if alvo == "":
                if contador == len(lista_alvos):
                    # se todos os tipos forem do mesmo tipo escolhe o primeiro:
                    alvo, tipo_arquivo = lista_alvos[0]
                    print("Todos os tipo são idênticos, escolhendo primeiro:", alvo)
                # prioriza alvo detectado com detect_rom se apenas foi um
                elif len(lista_index_rom_detectadas_com_detect_rom) == 1:
                    # utiliza esse index como o alvo
                    index = lista_index_rom_detectadas_com_detect_rom[0]
                    alvo, tipo_arquivo = lista_alvos[index]
                    print("Selecionado o alvo determinado por detect_rom:", alvo)
        if alvo == "":
            # recorre a escolha manual
            alvo, tipo_arquivo = escolha_manual(lista_alvos, ("Sair do programa", "Nenhum destes..."))
            # checa se escolheu sair do programa
            if tipo_arquivo == "Nenhum destes...":
                exit(0)
            print("alvo selecionado:", alvo)
            print("tipo alvo:", tipo_arquivo)
    # localiza arquivos salvos se existirem
    saves_dir = path.join(".", "saves")
    arquivo_save = None
    if path.exists(saves_dir):
        lista_saves = list()
        for arquivo in listdir(saves_dir):
            if arquivo.startswith(path.basename(caminho_arquivo) + "_save_"):
                lista_saves.append(path.join(saves_dir, arquivo))
        if len(lista_saves) > 0:
            print("foram localizados saves para este arquivo, deseja carregar?")
            arquivo_save = escolha_manual(lista_saves, "Nenhum")
            if arquivo_save == "Nenhum":
                arquivo_save = None
    # descompactador ja foi adquirido assim como listas_nome_crc32
    processa_arquivo(caminho_arquivo, tipo_arquivo, descompactador, alvo, listas_nome_crc32_tipos[:2], arquivo_save)


def converte_tipo_em_chave(tipo_detect_rom):
    global manual
    # resolve caso base
    if tipo_detect_rom == "Desconhecido":
        return "Desconhecido"
    # todas as chaves que contenham tipo_detect_rom como parte da prória chave
    chaves_contendo_substring = [chave for chave in dados_tipo.keys() if tipo_detect_rom in chave]
    # checa se a lista é maior do que um item
    if len(chaves_contendo_substring) > 1:
        # a lista tem varios itens
        if not manual:
            # reduz a lista de chaves a que tem o * na frente (escolha padrão).
            chaves_contendo_substring = [chave for chave in chaves_contendo_substring if chave.startswith("*")]
            return chaves_contendo_substring[0]
        else:
            # faz seleção manual
            tipo_arquivo = escolha_manual(chaves_contendo_substring, "Sair...")
            if tipo_arquivo == "Sair...":
                print("Saindo...")
                exit(0)
            return tipo_arquivo
    elif len(chaves_contendo_substring) == 1:
        # a lista so tem um item
        return chaves_contendo_substring[0]
    else:
        # a lista esta vazia, sai com erro
        print("Erro! Não foi possível converter chave em tipo, bug interno...")
        exit(1)


def checa_se_abre_arquivador(caminho_arquivo):
    if not config_dict["abre_arquivador"] == "":
        print("Não foi encontrado nenhum tipo reconhecido, iniciando arquivador padrão...")
        # se houver um arquivador configurado, abre ele para mostar o conteudo deste arquivo compactado
        subproc_run([config_dict["abre_arquivador"], caminho_arquivo], shell=False)
        exit(0)
    else:
        # se nao encontrar uma rom válida termina
        print(
            "Não foi encontraddo nenhum tipo conhecido no arquivo compactado, abortando..."
        )
        input("Enter para sair...")
        exit(1)


# metodo main - mostra versão atual e crédito, cria readme.txt se não existir ainda, inicializa e argparser e realiza
# as checagens dos parâmetros fornecidos, checa arquivos e caminhos fornecidos são válidos, verifica se o arquivo
# args.caminho_arquivo é compactado a partir da extensão ou se é de um tipo reconhecido.
def main():
    global manual
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

    # extensões suportadas
    lista_extensoes = list(descompactadores.keys())
    # print("extensões suportadas:", lista_extensoes)

    # pergunta ao usuario se quer escolha manual
    timeout = 2
    print("digite algo em %d segundos para habilitar escolha manual..." % timeout)
    inicio = time()
    tempo_decorrido = 0
    while tempo_decorrido < timeout:
        tempo_decorrido = time() - inicio
        escreve_contador_regressivo(tempo_decorrido, timeout)
        if tecla_foi_pressionada():
            # consome tecla
            le_tecla()
            manual = True
            print("\nEscolha manual habilitada.", end="")
            break
    # adiciona um \n para a ultima linha ter uma quebra corretamente
    print("")

    # Obtenha a extensão
    partes = path.basename(args.caminho_arquivo).lower().split('.')
    ext_arquivo = "." + ".".join(partes[1:])
    match partes[1:]:
        # arquivos compactados tipo .tar.gz
        case [*_, ext1, ext2] | [ext1, ext2] if "." + ext1 + "." + ext2 in lista_extensoes:
            if modo_debug:
                print("extensão encontrada a partir do nome:", "." + ext1 + "." + ext2)
            checa_arquivo_comprimido(args.caminho_arquivo, "." + ext1 + "." + ext2, ext2)
        # os outros tipos de arquivos compactados com apenas uma extensao
        case [*_, ext] if ("." + ext in lista_extensoes):
            if modo_debug:
                print("extensão encontrada a partir do nome:", "." + ext)
            checa_arquivo_comprimido(args.caminho_arquivo, "." + ext, ext)
        # arquivo não comprimido
        case _:
            if modo_debug:
                print("tratando arquivo fornecido como nao comprimido...")
            # tenta detectar tipo usando detect_rom primeiro
            detetor = DetectMagicBytes("conf/roms_mb.json")
            tipo_detect_rom = detetor.detecta_tipo_arquivo(args.caminho_arquivo)
            if tipo_detect_rom[0] != "Desconhecido":
                # converte em chave
                tipo_arquivo = converte_tipo_em_chave(tipo_detect_rom[0])
                # pega extensoes para esse tipo detectado
                exts = dados_tipo[tipo_arquivo]["ext"]
                # checa se a extensão do arquivo atual nao combina com o tipo
                if not path.splitext(args.caminho_arquivo)[1][1:].lower() in exts:
                    # nao combinou puxa pelo nome do arquivo mesmo
                    tipo_arquivo = tipo_do_nome_arquivo(args.caminho_arquivo)
                    print("tipo detectado com nome de arquivo:", tipo_arquivo)
                else:
                    print("tipo detectado com detect_rom(%s):" % args.caminho_arquivo, tipo_arquivo)
            else:
                # detect_rom nao detectou o arquivo tenta pelo nome de arquivo
                tipo_arquivo = tipo_do_nome_arquivo(args.caminho_arquivo)
                print("tipo detectado com nome de arquivo:", tipo_arquivo)
            # checa se o tipo é conhecido ja que tipo do nome pode retornar Desconhecido...
            if tipo_arquivo != "Desconhecido":
                # copia rom para diretorio temporario e executa pelo tipo
                processa_arquivo(args.caminho_arquivo, tipo_arquivo)
            else:
                # exibe mensagem informando que o arquivo é desconhecido...
                print("Arquivo comprimido não suportado ou não existe programa associado com a extensão:", ext_arquivo,
                      "tipo:", tipo_arquivo)
                input("Enter para sair...")


def checa_arquivo_comprimido(caminho_arquivo, ext_composta, ext_final):
    print("Extensão do arquivo fornecido:", ext_composta)
    # verifica se os arquivos são do tipo presumido
    detetor = DetectMagicBytes("conf/arcs_mb.json")
    tipo, magic_encoded = detetor.detecta_tipo_arquivo(caminho_arquivo)
    print("tipo do arquivo detectado:", tipo)
    if ext_final in tipo.lower():
        # chama encontra_e_processa_alvos o pre requisito é que o dicionario de descompacatores
        # possua uma entrada para o ipo especifico contendo um metodo para extrair os arquivos
        # e um metodo para listar todos os arquivo
        encontra_e_processa_alvos(ext_composta, caminho_arquivo)
    else:
        print("Erro! Arquivo compactado corrompido ou inválido.")
        exit(1)


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
    match PLATAFORMA:
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
        match PLATAFORMA:
            # inicia o ramdrive para as plataformas
            case "win32":
                inicia_imdisk_ramdisk(config_dict)
            case _:
                # se nao tem ramdrive nao tem como continuar ja que o caminho nao existe...
                print("Plataforma não suporta ramdrive...", PLATAFORMA)
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
    # Adicione o argumento 'caminho_arquivo' como opcional ja que ele pode não ser fornecido quando -h ou -r for
    # utilizado
    parser.add_argument('caminho_arquivo', nargs='?', help=caminho_text)
    # Parse dos argumentos
    args = parser.parse_args()
    # checa se o parametro -r foi utilizado
    if args.r:
        match PLATAFORMA:
            case "win32":
                remove_imdisk_ramdrive(config_dict)
                input("Enter para sair...")
                exit(0)
            case _:
                print("Plataforma não suporta esta operação...", PLATAFORMA)
    else:
        # se -r e -h não foi especificado entao caminho_arquivo é obrigatório para operação normal
        if args.caminho_arquivo is None:
            parser.error('O caminho_arquivo é obrigatório.')
    return args


# inicia o método main caso o programa seja iniciado pela linha de comando e não importado
if __name__ == '__main__':
    main()
