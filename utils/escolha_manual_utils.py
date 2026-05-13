# importar dicionario de config
from time import time
from sys import stdout as sys_stdout
from cria_json_inicial.config_dict import config_dict
import valores_globais
from plataforma.emu_rom_launcher_win32 import le_tecla_win32, tecla_foi_pressionada_win32


# implementação inicial do metodo que le apenas uma tecla, no momento apenas windows, se for linux ou outro usa input.
def le_tecla():
    if valores_globais.PLATAFORMA == 'win32':
        tecla = le_tecla_win32()
    else:
        print("Digite a opção e enter para confirmar: ", end="")
        tecla = input()
    return tecla


def tecla_foi_pressionada():
    if valores_globais.PLATAFORMA == 'win32':
        return tecla_foi_pressionada_win32()
    else:
        print("Erro - Ainda não possui implementação para tecla_foi_pressionada."
              "Plataforma %s ainda não suportada..." % valores_globais.PLATAFORMA)
        exit(1)


def escreve_contador_regressivo(tempo_decorrido, timeout):
    sys_stdout.write('\rTempo restante: %d ' % int(timeout - tempo_decorrido))
    sys_stdout.flush()


def pergunta_escolha_manual():
    # metodo que pergunta ao usuario se ele deseja configurar a escolha manual ou entao utiliza o valor global
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
            #atualiza variavel manual para True
            valores_globais.manual = True
            print("\nEscolha manual habilitada.", end="")
            break
    # adiciona um \n para a ultima linha ter uma quebra corretamente
    print("")


# exibe a lista de escolhas mostra um input perguntando a escolha correta
def escolha_manual(lista_escolhas, escolha_nao_aplicavel):
    # adiciona opcao escolha_nao_aplicavel ao fim da lista
    lista_escolhas.append(escolha_nao_aplicavel)

    # carrega valor timeout
    timeout = config_dict["tempo_espera_escolha"]
    # index da escolha padrão, -1 nao tem escolha padrao
    escolha_padrao = -1
    qtd_escolhas_padrao = 0

    tamanho_total_lista_escolhas = len(lista_escolhas)
    # workarround lista so com um caractere
    # limitacao de 36 itens por lista (10 numero + 26 letras do alfabeto)
    # inicializa numero de paginas e pagina atual como 0
    pagina_atual = 0
    # index de inicio da fatia
    if tamanho_total_lista_escolhas > 36:
        # lista muito grande, exbinido por paginas
        # listando os primeiro 35 itens da lista por pagina + rodape ate a ultima pagina
        # que pode conter ate 36 linhas...
        print('A quantidade de escolhas é maior que 36, mostrando apenas as primeiras 35...')
        tamanho_lista_escolhas = 35
        # teto da quantidade de linhas total divisão iteira por 36, subtrair 36 linhas do total antes e adicionar
        # +1 da pagina referente a esse 36 (qtd ultima pagina) no final.
        qtd_paginas = ((tamanho_total_lista_escolhas - 36 + tamanho_lista_escolhas - 1) // tamanho_lista_escolhas) + 1
    else:
        # ate 36 linhas na pagina
        tamanho_lista_escolhas = tamanho_total_lista_escolhas
        qtd_paginas = 1
    print("Existem %d escolhas possiveis:" % tamanho_total_lista_escolhas)
    if tamanho_lista_escolhas > 36:
        print("Exibindo por pagina, selecione z para proxima pagina...")

    letras = [chr(ord('a') + i) for i in range(26)]

    #inicializando inicio_fatia
    inicio_fatia = 0
    while True:
        fim_fatia = inicio_fatia + tamanho_lista_escolhas
        if fim_fatia > tamanho_total_lista_escolhas:
            fim_fatia = tamanho_total_lista_escolhas
        # cria copia da fatia lista escolhas para poder alterar os nomes
        lista_exibicao = lista_escolhas[inicio_fatia:fim_fatia]
        # checa se devemos escrever o rodape calculando o seguinte:
        # a quantidade de linhas que falta depois de ter escrito
        # tamanho_lista_escolha * pagina atual se nao faltar nada nao escreve o rodape.
        if inicio_fatia >= tamanho_lista_escolhas:
            lista_exibicao.append("Selecione para pagina anterior...")
        if tamanho_total_lista_escolhas - ((pagina_atual+1) * tamanho_lista_escolhas) > 0:
            lista_exibicao.append("Selecione para proxima pagina...")
        itens = [f"Item {i}" if i < 10 else f"Item {letras[i - 10]}" for i in range(len(lista_exibicao))]
        # encontra quantidade de opcoes com * na frente
        range_exibicao = range(len(lista_exibicao))
        for c in range_exibicao:
            # se alguma das alternativas é str e começa com * é escolha padrão, guarda este valor
            # if type(lista_escolhas[c]) == str and lista_escolhas[c][0] == "*":
            if valores_globais.debug:
                print("tipo do item:", type(lista_exibicao[c]), lista_exibicao[c])
            if type(lista_exibicao[c]) is str and lista_exibicao[c].startswith('*'):
                if valores_globais.debug:
                    print("escolha padrao encontrada removendo \"*\" do inicio:", lista_exibicao[c])
                # remove * do nome em lista_nomes
                lista_exibicao[c] = lista_exibicao[c][1:]
                escolha_padrao = c
                qtd_escolhas_padrao += 1
            # se for tupla e o segundo valor comecar com um * é a escolha padrão, guarda este valor
            # elif type(lista_escolhas[c]) == tuple and lista_escolhas[c][1][0] == "*":
            elif type(lista_exibicao[c]) is tuple and lista_exibicao[c][1].startswith('*'):
                # remove * do segundo item em lista_nomes
                lista_exibicao[c] = (lista_exibicao[c][0], lista_exibicao[c][1][1:])
                # sem escolha padrao para este tipo
                escolha_padrao = c
                qtd_escolhas_padrao += 1
        # mostra opções na tela
        for c in range_exibicao:
            # mostra opção na tela
            if qtd_escolhas_padrao == 1 and c == escolha_padrao:
                print("%s - %s <- escolha padrão" % (itens[c], lista_exibicao[c]))
            else:
                print("%s - %s" % (itens[c], lista_exibicao[c]))
        print("Qual opção você escolhe?")
        # prepara o loop e espera uma escolha valida
        escolha_index = -1
        inicio = time()
        # enquanto escolha_index nao estiver entre 0 e tamanho_listas_escolhas - 1 ou seja nao estiver sido selecionado.
        while not 0 <= escolha_index <= len(lista_exibicao) - 1:
            # inicia contagem de tempo se existir uma escolha padrão
            if qtd_escolhas_padrao == 1:
                tempo_decorrido = time() - inicio
                escreve_contador_regressivo(tempo_decorrido, timeout)
                # checa se o tempo do timeout ja passou
                if tempo_decorrido > timeout:
                    # acabou o tempo para escolher outra opção, executa usando a opção padrão
                    escolha_index = escolha_padrao
                    print("\nTimeout, escolhendo o padrão...", lista_exibicao[escolha_padrao], end="")
            # se alguma tecla foi pressionada le o valor
            if tecla_foi_pressionada():
                if qtd_escolhas_padrao == 1:
                    print("")
                tecla_digitada = le_tecla()
                # checa se é um digito numerico valido e seta escolha_index corretamente
                if tecla_digitada.isdigit() and 0 <= int(tecla_digitada) <= len(lista_exibicao) - 1:
                    escolha_index = int(tecla_digitada)
                    print("Escolhendo opção", lista_exibicao[escolha_index], end="")
                # checa se a opcao é uma letra e esta dentro das opcoes validas
                elif tecla_digitada.isalpha() and 0 <= ord(tecla_digitada) - 87 <= len(lista_exibicao) - 1:
                    escolha_index = ord(tecla_digitada) - 87
                    print("Escolhendo opção", lista_exibicao[escolha_index], end="")
                # checa se foi digitado "enter" e se há uma escolha padrão e nesse caso seleciona a escolha padrão
                elif ord(tecla_digitada) == 13 and qtd_escolhas_padrao == 1:
                    escolha_index = escolha_padrao
                    print("Escolhendo o padrão...", lista_exibicao[escolha_index], end="")
                else:
                    # qualquer outra coisa é tecla invalida
                    print("tecla invalida...", end="")
                    # se tiver em contagem adiciona um \n
                    if qtd_escolhas_padrao == 1:
                        print("")
        if lista_exibicao[escolha_index] == "Selecione para proxima pagina...":
            qtd_escolhas_restantes = tamanho_total_lista_escolhas - (pagina_atual * tamanho_lista_escolhas)
            # incrementar pagina atual
            pagina_atual += 1
            inicio_fatia = fim_fatia
            # novo valor para tamanho lista escolhas se tiver no meio do caminho
            # checa se quantidade é menor ou igual a 35
            # se for esse e o tamanho final da lista de escolhas
            if qtd_escolhas_restantes <= 35:
                tamanho_lista_escolhas = qtd_escolhas_restantes
            else:
                tamanho_lista_escolhas = 34
        elif lista_exibicao[escolha_index] == "Selecione para pagina anterior...":
            # decrementar pagina atual
            pagina_atual -= 1
            if pagina_atual == 0:
                # pagina inicial o tamanho eh 35
                tamanho_lista_escolhas = 35
                inicio_fatia = 0
            else:
                tamanho_lista_escolhas = 34
                inicio_fatia = inicio_fatia - tamanho_lista_escolhas
        else:
            # ja temos uma escolha selecionada em escolha_index...
            # adiciona quebra de linha para que o proximo print nao utilize a mesma linha ja que o sys.stdout nao adiciona \n
            # automaticamente
            print("")
            escolha_index_real = inicio_fatia + escolha_index
            return lista_escolhas[escolha_index_real]