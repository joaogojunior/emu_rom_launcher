from sys import platform as sys_platform
from os import path, mkdir

# modo debug
debug = True

# versao atual
VER = "0.1l"
# variavel que define o uso prioritario da escolha manual
manual = False
# encontra a plataforma atual
PLATAFORMA = sys_platform

# recriar conf se necessario
# cria arquivos de configuracao se necessario
if not path.isdir("conf"):
    mkdir("conf")

# importar dicionario de dados
from cria_json_inicial.dados_tipo_dict import dados_tipo

# remove tipo "help" do dicionario dados_tipo
dados_help = dados_tipo["help"]
del dados_tipo["help"]
# desvincula chave "caminhos"
caminhos = dados_tipo['caminhos']
del dados_tipo['caminhos']

# importar dicionario de config
from cria_json_inicial.config_dict import config_dict

# recria arcs_mb.json
from cria_json_inicial.arcs_mb_dict import arcs_mb_dict
# apaga o objeto ja queo arquivo ja foi recriado no caso de não existir
del arcs_mb_dict

# recria roms_mb_json
from cria_json_inicial.roms_mb_dict import roms_mb_dict
# apaga o objeto ja que o arquivo ja foi recriado no caso de não existir
del roms_mb_dict
