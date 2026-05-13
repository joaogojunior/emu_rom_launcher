from os import path, rename, makedirs
from typing import Literal, BinaryIO

from utils.crc32_utils import calcular_crc32_file_handle, calcular_crc32_bytes
from checa_magic.classe_checa_magic import ChecaMagic
import shutil
import valores_globais

from utils.subproc_bin import run_and_get_retval_stdout


# cria um arquivo .tar.xz a partir de uma lista de arquivos e o local onde estes arquivos estao
def criar_tar_xz(arquivo_saida, lista_arquivos, temp_dir):
    import tarfile
    with tarfile.open(arquivo_saida, "w:xz") as tar:
        for arquivo in lista_arquivos:
            # Adiciona cada arquivo à tarball
            caminho_completo = str(path.join(temp_dir, arquivo))
            tar.add(caminho_completo, arcname=arquivo)


# os metodos a seguir tem que seguir as seguintes conveções:
# metodo_extrair(arquivo_entrada, destino, alvo). Onde arquivo_entrada é o caminho completo para o arquivo compactado,
# destino é o caminho com nome de arquivo para o arquivo descompactado e alvo é o arquivo dentro do arquivo compactado
# que será extraido, alternativamente alvo pode ser "" significando que todos os arquivos devem ser extraidos e o
# caminho de destino é obtido a partir do dirname de destino.
# metodo_listar_conteudo(arquivo_entrada) e retorna lista de arquivos que estão contidos no arquivo de entrada. Onde
# arquivo_entrada é o caminho completo para o arquivo compactado.

# to dos: ZOO

# instancia detetor de roms
detetor = ChecaMagic("conf/roms_mb.json")


def mostra_erro_e_sai(erro, nome_arquivo):
    print("Erro! Não foi possivel abrir ou extrair um ou mais arquivos de %s." % nome_arquivo)
    print("Arquivo comprimido inválido ou corrompido. Detalhes do erro:", erro)
    input("Enter para sair...")
    exit(1)


# # suporte zip
# # funcao que lista o conteudo de um arquivo zip e uma lista com todos os checksums crc32
# def listar_conteudo_zip(arquivo_zip, detecta_tipos=True):
#     from zipfile import ZipFile
#     with ZipFile(arquivo_zip, 'r') as zip_ref:
#         try:
#             # Lista todos os arquivos e diretórios no arquivo zip
#             # a lista de arquivos no zip internamente tem o separador "/" inclusive no windows
#             # a lista tem que ser mantida como original poder referenciar os arquivo corretamente
#             # ao extrair, serao utilizadas os separadores corretos para o sistema operacional.
#             # lista_nomes_arquivos = zip_ref.namelist()
#             lista_nomes_arquivos = list()
#             lista_crc32 = list()
#             lista_tipos_detectados = list()
#             for info in zip_ref.infolist():
#                 # adiciona nome de arquvio a lista (diretorios ja vem com / no final)
#                 lista_nomes_arquivos.append(info.filename)
#                 if info.is_dir():
#                     # ja que é diretorio adiciona uma entrada vazia
#                     lista_crc32.append(0)
#                     # adiciona tipo correto
#                     lista_tipos_detectados.append(("Diretorio", b""))
#                 else:
#                     with zip_ref.open(info.filename) as arquivo_no_zip:
#                         lista_crc32.append(calcular_crc32_file_handle(arquivo_no_zip))
#                         if detecta_tipos:
#                             lista_tipos_detectados.append(detetor.detecta_tipo(arquivo_no_zip))
#                         else:
#                             lista_tipos_detectados.append(("Arquivo", b""))
#             # return conteudo
#             return lista_nomes_arquivos, lista_crc32, lista_tipos_detectados
#         except Exception as e:
#             mostra_erro_e_sai(str(e), arquivo_zip)
#
#
# # funcao que extrai arquivos de um zip
# def extrair_arquivo_zip(arquivo_zip, destino_dir, arquivo_saida="", alvo=""):
#     from zipfile import ZipFile
#     # remove arquivo de saida do destino
#     with ZipFile(arquivo_zip, 'r') as zip_ref:
#         try:
#             if alvo != "":
#                 # extrai apenas um arquivo
#                 # Extrai o arquivo específico para o diretório temporário
#                 zip_ref.extract(alvo, destino_dir)
#                 # renomeia arquivo para nome fornecido
#                 if arquivo_saida != alvo:
#                     rename(path.join(destino_dir, alvo), path.join(destino_dir, arquivo_saida))
#             else:
#                 # extrai todos arquivos
#                 # esse metodo extractall nao extrai diretorios vazios
#                 # entao os diretorios (arquivos terminados com "/" no nome) serao criados
#                 # manualmente
#                 # zip_ref.extractall(destino_dir)
#                 for info in zip_ref.infolist():
#                     # No padrão ZIP, entradas que terminam em '/' são diretórios
#                     if info.filename.endswith('/'):
#                         diretorio = str(info.filename)
#                         # como zip utiliza "/" internamente se for windows converte
#                         if valores_globais.PLATAFORMA == "win32":
#                             diretorio = diretorio.replace("/", "\\")
#                         caminho_pasta = path.join(destino_dir, diretorio)
#                         if valores_globais.debug:
#                             print("criando pasta manualmente:", diretorio)
#                         makedirs(caminho_pasta, exist_ok=True)
#                     else:
#                         # Extrai arquivos individuais normalmente
#                         zip_ref.extract(info, destino_dir)
#         except Exception as e:
#             mostra_erro_e_sai(str(e), arquivo_zip)


# from py7zr import SevenZipFile, WriterFactory
# import io

# supoerte 7z
# funcao que lista o conteudo de um arquivo 7z e uma lista com todos os checksums crc32
# 1. Defina um Factory para capturar os arquivos em memória
# class DictFactory(WriterFactory):
#     def __init__(self):
#         self.files = {}
#
#     def create(self, filename):
#         # Cria um buffer na memória para cada arquivo
#         self.files[filename] = io.BytesIO()
#         return self.files[filename]
#
#     def get_dict(self):
#         return self.files
#
# def listar_conteudo_7z(arquivo_7z):
#     # ajuda que o 7zip tambem utiliza / como separadoares assim como o zip
#     # porem ele dificulta obter os diretorios vazios
#     # so importa modulo do arquivo compactado quando for usa-lo
#     with SevenZipFile(arquivo_7z, mode='r') as ref_arq_7z:
#         # Lista todos os arquivos no arquivo 7zip
#         lista_nomes_arquivos = ref_arq_7z.getnames()
#         print(lista_nomes_arquivos)
#         lista_crc32 = list()
#         lista_tipos_detectados = list()
#
#         # 2. Use o factory para extrair direto para o dicionário
#         factory = DictFactory()
#         ref_arq_7z.extractall(factory=factory)
#         dict_arquivos_no_7z = factory.get_dict()
#
#         # read aqui retorna um dicionario com o nome do arquivo como chave e BytesIO como item
#         # dict_arquivos_no_7z = ref_arq_7z.read(lista_nomes_arquivos)
#         # aparentemente o 7z nao retorna a lista de nomes de maneira ordenada...
#         lista_nomes_arquivos.sort()
#         for c in range(len(lista_nomes_arquivos)):
#             nome_arquivo = lista_nomes_arquivos[c]
#             try:
#                 # como BytesIO é praticamente um file handler que suporta .read() usamos o metodo para file handler
#                 lista_crc32.append(calcular_crc32_file_handle(dict_arquivos_no_7z[nome_arquivo]))
#                 lista_tipos_detectados.append(detetor.detecta_tipo(dict_arquivos_no_7z[nome_arquivo]))
#             except KeyError:
#                 # se entrar aqui é pq eh um subdiretorio sem stream de bytes entao cria uma entrada vazia
#                 lista_crc32.append(0)
#                 lista_tipos_detectados.append(("Diretorio", b""))
#                 # adiciona "/" ao final do nome do diretorio como no zip
#                 lista_nomes_arquivos[c] = nome_arquivo + "/"
#         return lista_nomes_arquivos, lista_crc32, lista_tipos_detectados
#
#
# # funcao que extrai arquivos de um 7z
# def extrair_arquivo_7zip(arquivo_7zip, destino_dir, arquivo_saida="",  alvo=""):
#     from py7zr import SevenZipFile
#     # remove arquivo de saida do destino
#     with SevenZipFile(arquivo_7zip, mode='r') as zip_ref:
#         try:
#             if alvo != "":
#                 # extrai apenas um arquivo
#                 # Extrai o arquivo específico para o diretório temporário
#                 zip_ref.extract(targets=[alvo], path=destino_dir)
#                 # renomeia arquivo para arquivo_saida
#                 if arquivo_saida != alvo:
#                     rename(path.join(destino_dir, alvo), path.join(destino_dir, arquivo_saida))
#             else:
#                 # extrai todos arquivos
#                 zip_ref.extractall(path=destino_dir)
#         except Exception as e:
#             mostra_erro_e_sai(str(e), arquivo_7zip)

# suporte 7zip (.7z)
# funcao que lista o conteudo de um arquivo 7z
def listar_conteudo_com_7z(arquivo_compactado, detecta_tipos=True):

    cmd = valores_globais.config_dict["caminho_7zip"]
    param_list = "l"
    param_extract = "x"
    param_stdout = "-so"

    comando = [cmd, param_list, arquivo_compactado]
    # run_and_get_retval_stdout retorna um inteiro e um lista de bytes
    retval, bytes_lidos, _erro = run_and_get_retval_stdout(comando)
    if retval > 0:
        exit(1)
    if valores_globais.debug:
        print("resultado output:", bytes_lidos.split(b"\n"))
    # convertendo string bytes em utf-8
    lista_arquivos_atributos = list(map(lambda y: (y[53:].decode("utf-8").strip(), y[20:25]), bytes_lidos.split(b"\n")[19:-3]))
    if valores_globais.debug:
        print("lista arquivos:", lista_arquivos_atributos)
    lista_arquivos = list()
    lista_crc32 = list()
    lista_tipos_detectados = list()
    # no 7z os diretorios vem por ultimo e o separador eh "\" no windows
    # por isso obtem ao inverso a lista
    # lista de diretorios encontrados
    for arquivo, atributos in lista_arquivos_atributos:
        lista_arquivos.append(arquivo.replace("\\", "/"))
        # se for diretorio os atributos vem assim: b'D....'
        # por algum motivo o casting do python converte 1 byte para int
        if atributos[0] == 68: #68 ascii "D"
            lista_crc32.append(0)
            lista_tipos_detectados.append(("Diretorio", b""))
        else:
            comando2 = [cmd, param_extract, param_stdout, arquivo_compactado, arquivo]
            retval, bytes_arquivo, _erro = run_and_get_retval_stdout(comando2)
            # calcula crc32 a partir dos bytes
            lista_crc32.append(calcular_crc32_bytes(bytes_arquivo))
            if detecta_tipos:
                # detecta tipo com detect_rom
                lista_tipos_detectados.append(detetor.detecta_tipo(bytes_arquivo))
            else:
                lista_tipos_detectados.append(("Arquivo", b""))

    if valores_globais.debug:
        print("resultado final:",  lista_arquivos, lista_crc32, lista_tipos_detectados)
    return lista_arquivos, lista_crc32, lista_tipos_detectados


# funcao que extai o conteudo de um aqruivo 7z
def extrair_arquivo_com_7zip(arquivo_compactado, destino_dir, arquivo_saida="", alvo=""):
    cmd = "C:\\Program Files\\7-Zip\\7z.exe"
    param_extract = "x"
    param_output_dir = "-o"
    # remove arquivo de saida do destino
    if alvo != "":
        # extrai apenas um arquivo
        # verifica se alvo tem "/" e converte para "\" (separador de diretorios padrao no 7z
        if alvo.find("/") != -1:
            # adiciona "." no fim do arquivo para acessar corretamente
            alvo = alvo.replace("/", "\\")
        comando = [cmd, param_extract, arquivo_compactado, alvo]
        retval, bytes_arquivo, _erro = run_and_get_retval_stdout(comando)
        # Extrai o arquivo específico para o diretório temporário
        destino = path.join(destino_dir, arquivo_saida)
        if not path.isdir(destino_dir):
            makedirs(destino_dir, exist_ok=True)
        if retval == 0:
            with open(destino, "wb") as arquivo_destino:
                arquivo_destino.write(bytes_arquivo)
        else:
            print("Erro: comando %s falhou." %" ".join(comando))
            input("Enter para sair...")
            exit(1)
    else:
        # # cria diretorio de destino se ele nao existir
        # if not path.isdir(destino_dir):
        #     makedirs(destino_dir, exist_ok=True)
        # extrai todos arquivos
        comando = [cmd, param_extract, param_output_dir+destino_dir, arquivo_compactado]
        # subproc_run(comando, shell=False, capture_output=True, text=True)
        run_and_get_retval_stdout(comando)


# suporte pma (.lha)
# funcao que lista o conteudo de um arquivo pma
def listar_conteudo_pma(arquivo_pma, detecta_tipo=True):
    comando = ["./tools/lha", "-l", arquivo_pma]
    # resultado = subproc_run(comando, shell=False, capture_output=True, text=True)
    retval, stdout, stderr = run_and_get_retval_stdout(comando)
    if valores_globais.debug:
        print("resultado output:", stdout.decode(valores_globais.config_dict["encoding_padrao"]).split("\n"))
    lista_arquivos = list(map(lambda y: y.split(" ")[-1], stdout.split("\n")[2:-3]))
    if valores_globais.debug:
        print("lista arquivos:", lista_arquivos)
    # no pma arquivos sem extensão aparecem com o "." no fim do arquivo, que vai ser removido antes do return pois
    # aparentemente o "." é necessáiro para acessar o arquivo corretamente.
    lista_crc32 = list()
    lista_tipos_detectados = list()
    for arquivo in lista_arquivos:
        # se for diretorio tem / no fim e adiciona entrada de diretorio
        if arquivo.endswith("/"):
            lista_crc32.append(0)
            lista_tipos_detectados.append(("Diretorio", b""))
        else:
            comando2 = ["./tools/lha", "-pq", arquivo_pma, arquivo]
            # resultado = subproc_run(comando2, shell=False, capture_output=True, text=False)
            # # bytes_arquivo = resultado.stdout
            # if valores_globais.PLATAFORMA == "win32":
            #     bytes_arquivo = resultado.stdout.replace(b'\r\n', b'\n')
            # else:
            #     bytes_arquivo = resultado.stdout
            # # print(bytes_arquivo)
            retval, bytes_arquivo, _stderr = run_and_get_retval_stdout(comando2)
            # calcula crc32 a partir do bytes
            lista_crc32.append(calcular_crc32_bytes(bytes_arquivo))
            if detecta_tipo:
                # detecta tipo com detect_rom
                lista_tipos_detectados.append(detetor.detecta_tipo(bytes_arquivo))
            else:
                lista_tipos_detectados.append(("Arquivo", b""))
    # remove "." do fim do arquivo se houver
    lista_arquivos = list(map(lambda x: x[:-1] if x[-1] == "." else x, lista_arquivos))
    return lista_arquivos, lista_crc32, lista_tipos_detectados


# funcao que extai o conteudo de um aqruivo pma
def extrair_arquivo_pma(arquivo_pma, destino_dir, arquivo_saida="", alvo=""):
    # from subprocess import run as subproc_run
    # remove arquivo de saida do destino
    if alvo != "":
        # extrai apenas um arquivo
        # verifica se alvo tem "." no nome se nao tiver adiciona ao fim
        if alvo.find(".") == -1:
            # adiciona "." no fim do arquivo para acessar corretamente
            alvo += "."
        comando = ["./tools/lha", "-pq", arquivo_pma, alvo]
        # resultado = subproc_run(comando, shell=False, capture_output=True, text=False)
        retval, bytes_arquivo, _erro = run_and_get_retval_stdout(comando)
        # por algum bug (ou feature?) em subproc.run quando capiturado o stdout todas as ocorrencias de 0a estao sendo
        # substituidas por 0d 0a pelo menos no windows. Isso nao deveria ocorrer em arquivos binarios e sim em arquivos
        # textos entre dos (também windows) e unix. Mesmo com text=False acima nao impede isso de ocorrer mas faz stdout
        # receber uma byte string com esse bug, se text=True ele retorna None (provavelmente por que o utf8 nao consegue
        # codificar de maneira valida uma byte string)
        # if valores_globais.PLATAFORMA == "win32":
        #     # Remove '\r' antes de cada '\n' no windows
        #     bytes_arquivo = resultado.stdout.replace(b'\r\n', b'\n')
        # else:
        #     bytes_arquivo = resultado.stdout
        # Extrai o arquivo específico para o diretório temporário
        destino = path.join(destino_dir, arquivo_saida)
        if not path.isdir(destino_dir):
            makedirs(destino_dir, exist_ok=True)
        if retval == 0:
            with open(destino, "wb") as arquivo_destino:
                arquivo_destino.write(bytes_arquivo)
        else:
            print("Erro: comando %s falhou." %" ".join(comando))
            input("Enter para sair...")
            exit(1)
    else:
        # # cria diretorio de destino se ele nao existir
        # if not path.isdir(destino_dir):
        #     makedirs(destino_dir, exist_ok=True)
        # extrai todos arquivos
        comando = ["./tools/lha", "-xw=" + destino_dir, arquivo_pma]
        # subproc_run(comando, shell=False, capture_output=True, text=True)
        run_and_get_retval_stdout(comando)

# suporte .arj
# funcao que lista o conteudo de um arquivo arj
def listar_conteudo_arj(arquivo_arj, detecta_tipos=True):
    # arquivos arj funcionam bem diferentes de zip
    # diretorios sao separados por "\\" ao invez de "/"
    # from subprocess import run as subproc_run
    comando = ["./tools/unarj", "t", arquivo_arj]
    # resultado = subproc_run(comando, shell=False, capture_output=True, text=True)
    retval, saida, erro = run_and_get_retval_stdout(comando)
    lista_resultado = saida.decode(valores_globais.config_dict["encoding_padrao"]).split("\n")[5:-2]
    lista_resultado = list(map(lambda y: y.split(" "), lista_resultado))
    # lista_arquivos = sorted(lista_arquivos[7: -3])
    lista_arquivos_bruto = list()
    # em arquivo comprimidos o padrao zip eh /
    # troca \\ por / para os nomes de cada arquivo encontrado
    for linha in lista_resultado:
        # adiciona arquivo
        if linha[0] == "Testing":
            lista_arquivos_bruto.append(linha[4])
        # adiciona diretorio, usando / para diferenciar diretorio
        elif linha[0] == "Unsupported":
            lista_arquivos_bruto.append(linha[5]  + "\\")
    # print(lista_arquivos_bruto)
    # no pma arquivos sem extensão aparecem com o "." no fim do arquivo, que vai ser removido antes do return pois
    # aparentemente o "." é necessáiro para acessar o arquivo corretamente.
    lista_crc32 = list()
    lista_tipos_detectados = list()
    lista_nomes_arquivos = list()
    for arquivo in lista_arquivos_bruto:
        # verifica se eh um diretorio
        if arquivo.endswith("\\"):
            # eh um diretorio
            lista_crc32.append(0)
            lista_tipos_detectados.append(("Diretorio", b""))
            # troca o separador para o padrao "zip"
            lista_nomes_arquivos.append(arquivo.replace("\\", "/"))
        else:
            # eh um arquivo regular
            # aqui tem que utilizar o padrao arj apenas o arquivo sem caminho
            comando2 = ["./tools/unarj", "o", arquivo_arj, path.basename(arquivo)]
            # resultado = subproc_run(comando2, shell=False, capture_output=True, text=False)
            # if valores_globais.PLATAFORMA == "win32":
            #     bytes_arquivo = resultado.stdout.replace(b'\r\n', b'\n')
            # else:
            #     bytes_arquivo = resultado.stdout
            #
            # print(bytes_arquivo)
            retval, bytes_arquivo, erro = run_and_get_retval_stdout(comando2)
            # calcula crc32 a partir do bytes
            lista_crc32.append(calcular_crc32_bytes(bytes_arquivo))
            if detecta_tipos:
                # detecta tipo com detect_rom
                lista_tipos_detectados.append(detetor.detecta_tipo(bytes_arquivo))
            else:
                lista_tipos_detectados.append(("Arquivo", b""))
            # adiciona nome de arquivo com padrao convertido para zip
            lista_nomes_arquivos.append(arquivo.replace("\\", "/"))
            # se tiver um subdiretorio antes do nome de arquivo tenta adicionar ele tambem
            if arquivo.find("\\") != -1:
                # pega o subdiretorio inicial
                subdir = arquivo.split("\\")[0]
                # so adiciona se nao existir
                if not subdir + "/" in lista_nomes_arquivos:
                    # adiiona tambem o subdiretorio
                    lista_crc32.append(0)
                    lista_tipos_detectados.append(("Diretorio", b""))
                    # troca o separador para o padrao "zip"
                    lista_nomes_arquivos.append(subdir + "/")
    return lista_nomes_arquivos, lista_crc32, lista_tipos_detectados


# funcao que extai o conteudo de um aqruivo arj
def extrair_arquivo_arj(arquivo_arj, destino_dir, arquivo_saida="", alvo=""):
    # remove arquivo de saida do destino
    if alvo != "":
        extrai_apenas_um_arquivo_com_unarj(arquivo_arj, destino_dir, arquivo_saida, alvo)
    else:
        # extrai todos arquivos
        # obtem lista de arquivos
        lista_arquivo_no_arj = listar_conteudo_arj(arquivo_arj)[0]
        # extrai todos arquivos
        for arquivo in lista_arquivo_no_arj:
            dir_name_arquivo = str(path.dirname(arquivo).replace("/", "\\"))
            destino_dir_ok = path.join(destino_dir, dir_name_arquivo)
            arquivo_saida = path.basename(arquivo)
            extrai_apenas_um_arquivo_com_unarj(arquivo_arj, destino_dir_ok, arquivo_saida, arquivo)


def extrai_apenas_um_arquivo_com_unarj(arquivo_arj, destino_dir, arquivo_saida, alvo):
    # from subprocess import run as subproc_run
    # so executa o comando unarj se for em um arquivo, ja que diretorios nao sao suportados
    # pelo unarj.
    if not alvo.endswith("/"):
        # extrai apenas um arquivo usa apenas o nome do arquivo como "chave"
        comando = ["./tools/unarj", "o", arquivo_arj, path.basename(alvo)]
        # resultado = subproc_run(comando, shell=False, capture_output=True, text=False)
        # por algum bug todas as ocorrencias de 0a estao sendo substituidas por 0d 0a isso nao deveria ocorrer em
        # arquivos binarios, mas ocorre em arquivos textos entre dos (também windows) e unix.
        # Remove '\r' antes de cada '\n'
        # if valores_globais.PLATAFORMA == "win32":
        #     bytes_arquivo = resultado.stdout.replace(b'\r\n', b'\n')
        # else:
        #     bytes_arquivo = resultado.stdout
        retval, bytes_arquivo, _erro = run_and_get_retval_stdout(comando)
        # arquivo de saida
        # alvo_dir_name = path.dirname(alvo)
        # tive que desligar pq quebrava o teste
        # destino_dir = str(path.join(destino_dir, alvo_dir_name))
        destino = path.join(destino_dir, arquivo_saida)
        # cria subdiretorio intermediario, se necessario
        if not path.isdir(destino_dir):
            makedirs(destino_dir, exist_ok=True)
        # so cria arquivo de saida se o comando do unarj foi completado com sucesso
        if retval == 0:
            # escreve o conteudo obtido no arquivo de saida
            with open(destino, "wb") as arquivo_destino:
                arquivo_destino.write(bytes_arquivo)
        else:
            print("Erro: comando %s falhou." % " ".join(comando))
            input("Enter para sair...")
            exit(1)
    else:
        if not path.isdir(path.join(destino_dir, alvo)):
            # unarj nao extrai diretorios, simula com makedirs
            makedirs(path.join(destino_dir, alvo), exist_ok=True)


# funcao que lista o conteudo de um arquivo gzip
def listar_conteudo_gzip(arquivo_gzip, detecta_tipos=True):
    from gzip import open as gzip_open
    nome_arquivo = path.splitext(path.basename(arquivo_gzip))[0]
    with gzip_open(arquivo_gzip, 'rb') as arquivo_gz:
        crc32 = calcular_crc32_file_handle(arquivo_gz)
        if detecta_tipos:
            tipo = detetor.detecta_tipo(arquivo_gz)
        else:
            tipo = ("Arquivo", b"")
    return [nome_arquivo], [crc32], [tipo]


# funcao que lista o conteudo de um arquivo bzip2
def listar_conteudo_bzip2(arquivo_bzip2, detecta_tipos=True):
    from bz2 import open as bzip2_open
    nome_arquivo = path.splitext(path.basename(arquivo_bzip2))[0]
    with bzip2_open(arquivo_bzip2, 'rb') as arquivo_bz2:
        crc32 = calcular_crc32_file_handle(arquivo_bz2)
        if detecta_tipos:
            tipo = detetor.detecta_tipo(arquivo_bz2)
        else:
            tipo = ("Arquivo", b"")
    return [nome_arquivo], [crc32], [tipo]


# funcao que lista o conteudo de um arquivo xz
def listar_conteudo_xz(arquivo_xz, detecta_tipos=True):
    from lzma import open as xz_open
    nome_arquivo = path.splitext(path.basename(arquivo_xz))[0]
    with xz_open(arquivo_xz, 'rb') as handler_xz:
        crc32 = calcular_crc32_file_handle(handler_xz)
        if detecta_tipos:
            tipo = detetor.detecta_tipo(handler_xz)
        else:
            tipo = ("Arquivo", b"")
    return [nome_arquivo], [crc32], [tipo]


# funcao que extrai um arquivo de um gzip
def descompactar_gzip(arquivo_gzip, destino, _alvo=""):
    from gzip import open as gzip_open
    with gzip_open(arquivo_gzip, 'rb') as entrada, open(destino, 'wb') as saida:
        try:
            entrada: BinaryIO
            saida: BinaryIO
            shutil.copyfileobj(entrada, saida)
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_gzip)

# funcao que extrai um arquivo de um bzip2
def descompactar_bzip2(arquivo_bzip2, destino, _alvo=""):
    from bz2 import open as bzip2_open
    with bzip2_open(arquivo_bzip2, 'rb') as entrada, open(destino, 'wb') as saida:
        try:
            entrada: BinaryIO
            saida: BinaryIO
            shutil.copyfileobj(entrada, saida)
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_bzip2)

# funcao que extrai um arquivo de um xz
def descompactar_xz(arquivo_xz, destino, _alvo=""):
    # nesse caso alvo nao é necessário pois a informação já está em destino
    from lzma import open as xz_open
    with xz_open(arquivo_xz, 'rb') as entrada, open(destino, 'wb') as saida:
        try:
            entrada: BinaryIO
            saida: BinaryIO
            shutil.copyfileobj(entrada, saida)
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_xz)

# funcao que lista arquivos de um tar
def listar_conteudo_tar(arquivo_tar, detecta_tipos=True):
    from tarfile import open as tar_open
    with tar_open(arquivo_tar, 'r:*') as tar:
        try:
            # Lista todos os membros no arquivo .tar
            lista_nomes_arquivos = tar.getnames()
            lista_crc32 = list()
            lista_nomes_validos = list()
            lista_tipos_detectados = list()
            for nome_arquivo in lista_nomes_arquivos:
                # Usa getmember para verificar se é arquivo antes de extrair
                member = tar.getmember(nome_arquivo)
                if member.isfile():
                    arquivo_handler = tar.extractfile(member)
                    #arquivo_handler = tar.extractfile(nome_arquivo)
                    # devido ao tar informar entre os arquivos em getnames() tambem os subdiretorios, na hora de pagar um
                    # file handler eles retornao None detecta isso e cria uma noma lista de nomes apenas com os validos.
                    if arquivo_handler is not None:
                        lista_nomes_validos.append(nome_arquivo)
                        lista_crc32.append(calcular_crc32_file_handle(arquivo_handler))
                        if detecta_tipos:
                            lista_tipos_detectados.append(detetor.detecta_tipo(arquivo_handler))
                        else:
                            lista_tipos_detectados.append(("Arquivo", b""))
            return lista_nomes_validos, lista_crc32, lista_tipos_detectados
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_tar)


# funcao que extrai arquivos de um tar passando o modo (gz, bz2 ou xz)
def descompactar_tar(arquivo_tar: str, destino, alvo, modo: str=""):
    from tarfile import open as tar_open
    saida_arquivo = str(path.basename(destino))
    destino_dir = str(path.dirname(destino))
    # Abre o arquivo .tar.gz
    # corrige o typing do parametro modo chamando a funcao Tarfile.open
    modo_leitura: Literal["r", "r:*", "r:", "r:gz", "r:bz2", "r:xz"] = 'r:' + modo if modo else 'r'
    print(modo_leitura, arquivo_tar, destino_dir, alvo)
    with tar_open(arquivo_tar, mode=modo_leitura) as tar:
        try:
            if alvo != "":
                # Extrai o arquivo específico para o diretório temporário
                tar.extract(alvo, path=destino_dir, filter='fully_trusted')
                rename(path.join(destino_dir, alvo), path.join(destino_dir, saida_arquivo))
            else:
                tar.extractall(path=destino_dir, filter='fully_trusted')
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_tar)


# funcao que extrai arquivos de um tar.gz
def descompactar_tar_gz(arquivo_tar_gz, destino, alvo):
    descompactar_tar(arquivo_tar_gz, destino, alvo, "gz")


# funcao que extrai arquivos de um tar.bz2
def descompactar_tar_bz2(arquivo_tar_bz2, destino, alvo):
    descompactar_tar(arquivo_tar_bz2, destino, alvo, "bz2")


# funcao que extrai arquivos de um tar.xz
def descompactar_tar_xz(arquivo_tar_xz, destino, alvo):
    descompactar_tar(arquivo_tar_xz, destino, alvo, "xz")
