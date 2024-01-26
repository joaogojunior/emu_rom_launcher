from json import loads
from os import path


def carrega_ou_cria_config(arquivo, json_padrao):
    # testa se o arquivo de configuração existe
    if not path.exists(arquivo):
        # se nao existir cria um com os defaults
        print("Arquivo de configuração %s não encontrado, criando um com padrões..." % arquivo)
        with (open(arquivo, "w") as config):
            # carrega os padroes logo para nao ser necessario rodar o programa novamente
            config.write(json_padrao)
            return loads(json_padrao)
    else:
        return carrega_config(arquivo)


def carrega_config(arquivo):
    # carrega o arquivo de configuracao
    print("Carregando configurações de", arquivo + "...")
    with open(arquivo, "r") as config:
        return loads(config.read().strip())
