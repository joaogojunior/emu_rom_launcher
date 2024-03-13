from os import makedirs, path, rename
from crc32_utils import calcular_crc32_file_handle, calcular_crc32_bytes
from detect_rom import DetectMagicBytes
from sys import platform as sys_platform

# encontra a plataforma atual
PLATAFORMA = sys_platform

# os metodos a seguir tem que seguir as seguintes conveções:
# metodo_extrair(arquivo_entrada, destino, alvo). Onde arquivo_entrada é o caminho completo para o arquivo compactado,
# destino é o caminho com nome de arquivo para o arquivo descompactado e alvo é o arquivo dentro do arquivo compactado
# que será extraido, alternativamente alvo pode ser "" significando que todos os arquivos devem ser extraidos e o
# caminho de destino é obtido a partir do dirname de destino.
# metodo_listar_conteudo(arquivo_entrada) e retorna lista de arquivos que estão contidos no arquivo de entrada. Onde
# arquivo_entrada é o caminho completo para o arquivo compactado.

# to dos: ZOO

# instancia detetor de roms
detetor = DetectMagicBytes("conf/roms_mb.json")


# cria um arquivo .tar.xz a partir de uma lista de arquivos e o local onde estes arquivos estao
def criar_tar_xz(arquivo_saida, lista_arquivos, temp_dir):
    import tarfile
    with tarfile.open(arquivo_saida, "w:xz") as tar:
        for arquivo in lista_arquivos:
            # Adiciona cada arquivo à tarball
            caminho_completo = path.join(temp_dir, arquivo)
            tar.add(caminho_completo, arcname=arquivo)


def mostra_erro_e_sai(erro, nome_arquivo):
    print("Erro! Não foi possivel abrir ou extrair um ou mais arquivos de %s." % nome_arquivo)
    print("Arquivo comprimido inválido ou corrompido. Detalhes do erro:", erro)
    print("Digite enter para sair...")
    input()
    exit(1)


# funcao que lista o conteudo de um arquivo pma
def listar_conteudo_arj(arquivo_arj):
    from subprocess import run as subproc_run
    comando = ["./tools/unarj", "l", arquivo_arj]
    resultado = subproc_run(comando, shell=False, capture_output=True, text=True)
    # print(resultado.stdout.split("\n"))
    lista_arquivos = list(map(
        lambda y: y.split(" ")[0], resultado.stdout.split("\n")
    ))
    lista_arquivos = sorted(lista_arquivos[7: -3])
    # print(lista_arquivos)
    # no pma arquivos sem extensão aparecem com o "." no fim do arquivo, que vai ser removido antes do return pois
    # aparentemente o "." é necessáiro para acessar o arquivo corretamente.
    lista_crc32 = list()
    lista_tipos_detectados = list()
    for arquivo in lista_arquivos:
        comando2 = ["./tools/unarj", "o", arquivo_arj, arquivo]
        resultado = subproc_run(comando2, shell=False, capture_output=True, text=False)
        if PLATAFORMA == "win32":
            bytes_arquivo = resultado.stdout.replace(b'\r\n', b'\n')
        else:
            bytes_arquivo = resultado.stdout
        #
        # print(bytes_arquivo)
        # calcula crc32 a partir do bytes
        lista_crc32.append(calcular_crc32_bytes(bytes_arquivo))
        # detecta tipo com detect_rom
        lista_tipos_detectados.append(detetor.detecta_tipo_bytes(bytes_arquivo))
    # remove "." do fim do arquivo se houver
    # lista_arquivos = list(map(lambda x: x[:-1] if x[-1] == "." else x, lista_arquivos))
    return lista_arquivos, lista_crc32, lista_tipos_detectados


# funcao que extai o conteudo de um aqruivo pma
def extrair_arquivo_arj(arquivo_arj, destino, alvo=""):
    from subprocess import run as subproc_run
    # remove arquivo de saida do destino
    destino_dir = path.dirname(destino)
    if alvo != "":
        # extrai apenas um arquivo
        # verifica se alvo tem "." no nome se nao tiver adiciona ao fim
        # if alvo.find(".") == -1:
        #     # adiciona "." no fim do arquivo para acessar corretamente
        #     alvo += "."
        comando = ["./tools/unarj", "o", arquivo_arj, alvo]
        resultado = subproc_run(comando, shell=False, capture_output=True, text=False)
        # por algum bug todas as ocorrencias de 0a estao sendo substituidas por 0d 0a isso nao deveria ocorrer em
        # arquivos binarios, mas ocorre em arquivos textos entre dos (também windows) e unix.
        # Remove '\r' antes de cada '\n'
        if PLATAFORMA == "win32":
            bytes_arquivo = resultado.stdout.replace(b'\r\n', b'\n')
        else:
            bytes_arquivo = resultado.stdout
        # Extrai o arquivo específico para o diretório temporário
        with open(destino, "wb") as arquivo_destino:
            arquivo_destino.write(bytes_arquivo)
    else:
        # extrai todos arquivos
        comando = ["./tools/unarj", "x", arquivo_arj, destino_dir]
        subproc_run(comando, shell=False, capture_output=True, text=True)


# funcao que lista o conteudo de um arquivo pma
def listar_conteudo_pma(arquivo_pma):
    from subprocess import run as subproc_run
    comando = ["./tools/lha", "-t", arquivo_pma]
    resultado = subproc_run(comando, shell=False, capture_output=True, text=True)
    # print(resultado.stdout.split("\n"))
    lista_arquivos = sorted(list(set(map(
        lambda y: y.split("\t")[0], filter(lambda x: x != "", resultado.stdout.split("\n"))
    ))))
    # print(lista_arquivos)
    # no pma arquivos sem extensão aparecem com o "." no fim do arquivo, que vai ser removido antes do return pois
    # aparentemente o "." é necessáiro para acessar o arquivo corretamente.
    lista_crc32 = list()
    lista_tipos_detectados = list()
    for arquivo in lista_arquivos:
        comando2 = ["./tools/lha", "-pq", arquivo_pma, arquivo]
        resultado = subproc_run(comando2, shell=False, capture_output=True, text=False)
        # bytes_arquivo = resultado.stdout
        if PLATAFORMA == "win32":
            bytes_arquivo = resultado.stdout.replace(b'\r\n', b'\n')
        else:
            bytes_arquivo = resultado.stdout
        # print(bytes_arquivo)
        # calcula crc32 a partir do bytes
        lista_crc32.append(calcular_crc32_bytes(bytes_arquivo))
        # detecta tipo com detect_rom
        lista_tipos_detectados.append(detetor.detecta_tipo_bytes(bytes_arquivo))
    # remove "." do fim do arquivo se houver
    lista_arquivos = list(map(lambda x: x[:-1] if x[-1] == "." else x, lista_arquivos))
    return lista_arquivos, lista_crc32, lista_tipos_detectados


# funcao que extai o conteudo de um aqruivo pma
def extrair_arquivo_pma(arquivo_pma, destino, alvo=""):
    from subprocess import run as subproc_run
    # remove arquivo de saida do destino
    destino_dir = path.dirname(destino)
    if alvo != "":
        # extrai apenas um arquivo
        # verifica se alvo tem "." no nome se nao tiver adiciona ao fim
        if alvo.find(".") == -1:
            # adiciona "." no fim do arquivo para acessar corretamente
            alvo += "."
        comando = ["./tools/lha", "-pq", arquivo_pma, alvo]
        resultado = subproc_run(comando, shell=False, capture_output=True, text=False)
        # por algum bug (ou feature?) em subproc.run quando capiturado o stdout todas as ocorrencias de 0a estao sendo
        # substituidas por 0d 0a pelo menos no windows. Isso nao deveria ocorrer em arquivos binarios e sim em arquivos
        # textos entre dos (também windows) e unix. Mesmo com text=False acima nao impede isso de ocorrer mas faz stdout
        # receber uma byte string com esse bug, se text=True ele retorna None (provavelmente por que o utf8 nao consegue
        # codificar de maneira valida uma byte string)
        if PLATAFORMA == "win32":
            # Remove '\r' antes de cada '\n' no windows
            bytes_arquivo = resultado.stdout.replace(b'\r\n', b'\n')
        else:
            bytes_arquivo = resultado.stdout
        # Extrai o arquivo específico para o diretório temporário
        with open(destino, "wb") as arquivo_destino:
            arquivo_destino.write(bytes_arquivo)
    else:
        # extrai todos arquivos
        comando = ["./tools/lha", "-xw=" + destino_dir, arquivo_pma]
        subproc_run(comando, shell=False, capture_output=True, text=True)


# funcao que lista o conteudo de um arquivo gzip
def listar_conteudo_gzip(arquivo_gzip):
    from gzip import open as gzip_open
    nome_arquivo = path.splitext(path.basename(arquivo_gzip))[0]
    with gzip_open(arquivo_gzip, 'rb') as arquivo_gz:
        crc32 = calcular_crc32_file_handle(arquivo_gz)
        tipo = detetor.detecta_tipo_file_handler(arquivo_gz)
    return [nome_arquivo], [crc32], [tipo]


# funcao que lista o conteudo de um arquivo bzip2
def listar_conteudo_bzip2(arquivo_bzip2):
    from bz2 import open as bzip2_open
    nome_arquivo = path.splitext(path.basename(arquivo_bzip2))[0]
    with bzip2_open(arquivo_bzip2, 'rb') as arquivo_bz2:
        crc32 = calcular_crc32_file_handle(arquivo_bz2)
        tipo = detetor.detecta_tipo_file_handler(arquivo_bz2)
    return [nome_arquivo], [crc32], [tipo]


# funcao que lista o conteudo de um arquivo xz
def listar_conteudo_xz(arquivo_xz):
    from lzma import open as xz_open
    nome_arquivo = path.splitext(path.basename(arquivo_xz))[0]
    with xz_open(arquivo_xz, 'rb') as handler_xz:
        crc32 = calcular_crc32_file_handle(handler_xz)
        tipo = detetor.detecta_tipo_file_handler(handler_xz)
    return [nome_arquivo], [crc32], [tipo]


# funcao que extrai um arquivo de um gzip
def descompactar_gzip(arquivo_gzip, destino, _alvo=""):
    from gzip import open as gzip_open
    with gzip_open(arquivo_gzip, 'rb') as entrada, open(destino, 'wb') as saida:
        try:
            saida.write(entrada.read())
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_gzip)


# funcao que extrai um arquivo de um bzip2
def descompactar_bzip2(arquivo_bzip2, destino, _alvo=""):
    from bz2 import open as bzip2_open
    with bzip2_open(arquivo_bzip2, 'rb') as entrada, open(destino, 'wb') as saida:
        try:
            saida.write(entrada.read())
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_bzip2)


# funcao que extrai um arquivo de um xz
def descompactar_xz(arquivo_xz, destino, _alvo=""):
    # nesse caso alvo nao é necessário pois a informação já está em destino
    from lzma import open as xz_open
    with xz_open(arquivo_xz, 'rb') as entrada, open(destino, 'wb') as saida:
        try:
            saida.write(entrada.read())
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_xz)


# # funcao que lista o conteudo de um arquivo lzh
# def listar_conteudo_lzh_lhafile(arquivo_lzh):
#     from lhafile import Lhafile
#     try:
#         lzh_ref = Lhafile(arquivo_lzh, 'r')
#         lista_nomes_arquivos = lzh_ref.namelist()
#         lista_crc32 = list()
#         lista_nomes_validos = list()
#         lista_tipos_detectados = list()
#         for nome_arquivo in lista_nomes_arquivos:
#             # como o suporte a lha eh meia boca, nao tenho nem um file handler so mesmo os bytes do conteudo, ai não é
#             # possível usar a estratégia de ler 4k por vez, pois ja leu tudo! Utiliza calcular_crc32_bytes mesmo... :(
#             # pelos meus testes lha guarda subdiretorios com \ o padrao que eu tenho adotado é /, converte se for o
#             # caso...
#             bytes_arquivo = lzh_ref.read(nome_arquivo)
#             # calcula crc32 a partir do bytes
#             lista_crc32.append(calcular_crc32_bytes(bytes_arquivo))
#             # detecta tipo com detect_rom
#             lista_tipos_detectados.append(detetor.detecta_tipo_bytes(bytes_arquivo))
#             # em plataformas diferentes de windows a seguinte linha nao deve alterar nada
#             nome_arquivo = nome_arquivo.replace("\\", "/")
#             lista_nomes_validos.append(nome_arquivo)
#         del lzh_ref
#         return lista_nomes_validos, lista_crc32, lista_tipos_detectados
#     except Exception as e:
#         mostra_erro_e_sai(str(e), arquivo_lzh)


# funcao que lista o co nteudo de um arquivo 7z e uma lista com todos os checksums crc32
def listar_conteudo_7z(arquivo_7z):
    # so importa modulo do arquivo compactado quando for usa-lo
    from py7zr import SevenZipFile
    with SevenZipFile(arquivo_7z, mode='r') as ref_arq_7z:
        # Lista todos os arquivos no arquivo 7zip
        lista_nomes_arquivos = ref_arq_7z.getnames()
        lista_crc32 = list()
        lista_tipos_detectados = list()
        lista_nomes_validos = list()
        # read aqui retorna um dicionario com o nome do arquivo como chave e BytesIO como item
        dict_arquivos_no_7z = ref_arq_7z.read(lista_nomes_arquivos)
        # aparentemente o 7z nao retorna a lista de nomes de maneira ordenada...
        lista_nomes_arquivos.sort()
        for nome_arquivo in lista_nomes_arquivos:
            try:
                # como BytesIO é praticamente um file handler que suporta .read() usamos o metodo para file handler
                lista_crc32.append(calcular_crc32_file_handle(dict_arquivos_no_7z[nome_arquivo]))
                lista_tipos_detectados.append(detetor.detecta_tipo_file_handler(dict_arquivos_no_7z[nome_arquivo]))
                lista_nomes_validos.append(nome_arquivo)
            except KeyError:
                # se entrar aqui é pq eh um subdiretorio sem stream de bytes associado entao pode pular ele
                continue
        return lista_nomes_validos, lista_crc32, lista_tipos_detectados


# funcao que lista o conteudo de um arquivo zip e uma lista com todos os checksums crc32
def listar_conteudo_zip(arquivo_zip):
    from zipfile import ZipFile
    with ZipFile(arquivo_zip, 'r') as zip_ref:
        try:
            # Lista todos os arquivos e diretórios no arquivo zip
            lista_nomes_arquivos = zip_ref.namelist()
            lista_crc32 = list()
            lista_tipos_detectados = list()
            for nome_arquivo in lista_nomes_arquivos:
                with zip_ref.open(nome_arquivo) as arquivo_no_zip:
                    lista_crc32.append(calcular_crc32_file_handle(arquivo_no_zip))
                    lista_tipos_detectados.append(detetor.detecta_tipo_file_handler(arquivo_no_zip))
            # return conteudo
            return lista_nomes_arquivos, lista_crc32, lista_tipos_detectados
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_zip)


# funcao que lista arquivos de um tar
def listar_conteudo_tar(arquivo_tar):
    from tarfile import open as tar_open
    with tar_open(arquivo_tar, 'r') as tar:
        try:
            # Lista todos os membros no arquivo .tar
            lista_nomes_arquivos = tar.getnames()
            lista_crc32 = list()
            lista_nomes_validos = list()
            lista_tipos_detectados = list()
            for nome_arquivo in lista_nomes_arquivos:
                arquivo_handler = tar.extractfile(nome_arquivo)
                # devido ao tar informar entre os arquivos em getnames() tambem os subdiretorios, na hora de pagar um
                # file handler eles retornao None detecta isso e cria uma noma lista de nomes apenas com os validos.
                if arquivo_handler is not None:
                    lista_nomes_validos.append(nome_arquivo)
                    lista_crc32.append(calcular_crc32_file_handle(arquivo_handler))
                    lista_tipos_detectados.append(detetor.detecta_tipo_file_handler(arquivo_handler))
            return lista_nomes_validos, lista_crc32, lista_tipos_detectados
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_tar)


# funcao que lista o conteudo de um tar.gz
def listar_conteudo_tar_gz(arquivo_tar_gz):
    from tempfile import TemporaryDirectory
    from config_dict import config_dict
    with (TemporaryDirectory(dir=config_dict["caminho_temp_dir"]) as temp_dir):
        destino = path.join(temp_dir, path.splitext(path.basename(arquivo_tar_gz))[0])
        descompactar_gzip(arquivo_tar_gz, destino)
        lista_conteudo = listar_conteudo_tar(destino)
    return lista_conteudo


# funcao que lista o conteudo de um tar.bz2
def listar_conteudo_tar_bz2(arquivo_tar_bz2):
    from tempfile import TemporaryDirectory
    from config_dict import config_dict
    with (TemporaryDirectory(dir=config_dict["caminho_temp_dir"]) as temp_dir):
        destino = path.join(temp_dir, path.splitext(path.basename(arquivo_tar_bz2))[0])
        descompactar_bzip2(arquivo_tar_bz2, destino)
        lista_conteudo = listar_conteudo_tar(destino)
    return lista_conteudo


# funcao que lista o conteudo de um tar.xz
def listar_conteudo_tar_xz(arquivo_tar_xz):
    from tempfile import TemporaryDirectory
    from config_dict import config_dict
    with (TemporaryDirectory(dir=config_dict["caminho_temp_dir"]) as temp_dir):
        destino = path.join(temp_dir, path.splitext(path.basename(arquivo_tar_xz))[0])
        descompactar_xz(arquivo_tar_xz, destino)
        lista_conteudo = listar_conteudo_tar(destino)
    return lista_conteudo


# # funcao que extai o conteudo de um aqruivo lha (lzh)
# def extrair_arquivo_lzh_lhafile(arquivo_lzh, destino, alvo=""):
#     from lhafile import Lhafile
#     # remove arquivo de saida do destino
#     destino_dir = path.dirname(destino)
#     lzh_ref = Lhafile(arquivo_lzh, 'r')
#     try:
#         if alvo != "":
#             # extrai apenas um arquivo
#             # Extrai o arquivo específico para o diretório temporário
#             with open(destino, "wb") as arquivo_destino:
#                 arquivo_destino.write(lzh_ref.read(alvo))
#         else:
#             # extrai todos arquivos
#             # Itera sobre os arquivos no arquivo .lzh e extrai um por um
#             for caminho_arquivo in lzh_ref.namelist():
#                 # checa se um subdiretorio existe no dir temporario
#                 diretorio_arquivo = path.dirname(caminho_arquivo)
#                 if diretorio_arquivo == "":
#                     diretorio_arquivo = "."
#                 # Verifica se o diretório existe, se não, cria recursivamente
#                 caminho_para_checar = path.join(destino_dir, diretorio_arquivo)
#                 if not path.exists(caminho_para_checar):
#                     # se necessário cria diretorios
#                     makedirs(caminho_para_checar)
#                 # abre arquivo de destino e escreve ele
#                 with open(path.join(destino_dir, caminho_arquivo), 'wb') as arquivo_destino:
#                     arquivo_destino.write(lzh_ref.read(caminho_arquivo))
#     except Exception as e:
#         mostra_erro_e_sai(str(e), arquivo_lzh)
#     del lzh_ref


# funcao que extrai arquivos de um 7z
def extrair_arquivo_7zip(arquivo_7zip, destino, alvo=""):
    from py7zr import SevenZipFile
    # remove arquivo de saida do destino
    saida_arquivo = path.basename(destino)
    destino_dir = path.dirname(destino)
    with SevenZipFile(arquivo_7zip, mode='r') as zip_ref:
        try:
            if alvo != "":
                # extrai apenas um arquivo
                # Extrai o arquivo específico para o diretório temporário
                zip_ref.extract(targets=[alvo], path=destino_dir)
                # renomeia arquivo para cart.rom
                rename(path.join(destino_dir, alvo), path.join(destino_dir, saida_arquivo))
            else:
                # extrai todos arquivos
                zip_ref.extractall(path=destino_dir)
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_7zip)


# funcao que extrai arquivos de um zip
def extrair_arquivo_zip(arquivo_zip, destino, alvo=""):
    from zipfile import ZipFile
    # remove arquivo de saida do destino
    saida_arquivo = path.basename(destino)
    destino_dir = path.dirname(destino)
    with ZipFile(arquivo_zip, 'r') as zip_ref:
        try:
            if alvo != "":
                # extrai apenas um arquivo
                # Extrai o arquivo específico para o diretório temporário
                zip_ref.extract(alvo, destino_dir)
                # renomeia arquivo para cart.rom
                rename(path.join(destino_dir, alvo), path.join(destino_dir, saida_arquivo))
            else:
                # extrai todos arquivos
                zip_ref.extractall(destino_dir)
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_zip)


# funcao que extrai arquivos de um tar passando o modo (gz ou bz2)
def descompactar_tar(arquivo_tar_gz, destino, alvo, modo=""):
    from tarfile import open as tar_open
    saida_arquivo = path.basename(destino)
    destino_dir = path.dirname(destino)
    # Abre o arquivo .tar.gz
    with tar_open(arquivo_tar_gz, 'r:' + modo) as tar:
        try:
            if alvo != "":
                # Extrai o arquivo específico para o diretório temporário
                tar.extract(alvo, path=destino_dir)
                rename(path.join(destino_dir, alvo), path.join(destino_dir, saida_arquivo))
            else:
                tar.extractall(path=destino_dir)
        except Exception as e:
            mostra_erro_e_sai(str(e), arquivo_tar_gz)


# funcao que extrai arquivos de um tar.gz
def descompactar_tar_gz(arquivo_tar_gz, destino, alvo):
    descompactar_tar(arquivo_tar_gz, destino, alvo, "gz")


# funcao que extrai arquivos de um tar.bz2
def descompactar_tar_bz2(arquivo_tar_bz2, destino, alvo):
    descompactar_tar(arquivo_tar_bz2, destino, alvo, "bz2")


# funcao que extrai arquivos de um tar.xz
def descompactar_tar_xz(arquivo_tar_xz, destino, alvo):
    descompactar_tar(arquivo_tar_xz, destino, alvo, "xz")
