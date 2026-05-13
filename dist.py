# primeiro executa cria_json_inicial.gerar_arquivos_json_iniciais_a_partir_de_conf
from cria_json_inicial import gerar_arquivos_json_inciciais_a_partir_de_conf
gerar_arquivos_json_inciciais_a_partir_de_conf.cria_arquivos()
# # segundo copia arquivos para dist
# # copiar conf/ para dist
from os import environ #, makedirs, listdir
from utils.arquivo_util import copia_arquivo
# makedirs("dist/conf", exist_ok=True)
# lista_arquivos = listdir('conf')
# print(lista_arquivos)
# for arquivo in lista_arquivos:
#     copia_arquivo("conf/" + arquivo, "dist/conf/" + arquivo)
# # copiar tools/ para dist
# makedirs("dist/tools", exist_ok=True)
# lista_arquivos = listdir('tools')
# print(lista_arquivos)
# for arquivo in lista_arquivos:
#     copia_arquivo("tools/" + arquivo, "dist/tools/" + arquivo)

# copia readme.md
copia_arquivo("README.MD", "dist/README.MD")

# terceiro executar compila com pyinst
# setar variavel de ambiente para chamar compilacompyinst
environ.update([("USA_CONSOLE", "1"), ("UPX_DIR", "C:\\win apps\\compactador utils\\upx-4.2.4-win64"),
                ])

from subprocess import run as subproc_run
subproc_run(["python", "..\\compila_com_pyinstaller\\compila_com_pyinstaller.py", ".\\detect_rom.py", ".\\emu_rom_launcher.py"])
# apaga arquivo .\dist\dist.zip antigo
subproc_run(["cmd", "/c", "del", ".\\dist\\dist.zip"])
# por ultimo cria um zip com tudo
subproc_run(["C:\\Program Files\\7-Zip\\7z.exe", "a", "-tzip", "-r", "dist\\dist.zip", ".\\dist\\"])