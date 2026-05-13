import valores_globais
from os import path, walk


def lista_todos_arquivos_no_caminho(caminho_raiz, relativo=False, inclui_subdirs=False, posix=False):
    retorno_lista_arquivos_no_diretorio = []
    for caminho_atual, subpastas, arquivos_na_pasta in walk(caminho_raiz):
        for nome_arquivo in arquivos_na_pasta:
            caminho_atual_ok = caminho_atual[:]
            if relativo:
                caminho_atual_ok = path.relpath(caminho_atual, caminho_raiz)
                # ignora entrada "."
                if caminho_atual_ok == ".":
                    caminho_atual_ok = ""
            # resolve typing do parametro caminho_completo evitando uso implicito de bytes
            caminho_arquivo_atual = str(path.join(caminho_atual_ok, nome_arquivo))
            # essa parte eh util ao gerar lista de arquivos comparaveis com as listas
            # obtidas anteriormente dos arquivos comprimidos
            if posix and valores_globais.PLATAFORMA == "win32":
                # reformata a string para usar / como separador de diretorios
                caminho_arquivo_atual = caminho_arquivo_atual.replace("\\", "/")
            retorno_lista_arquivos_no_diretorio.append(caminho_arquivo_atual)
        else:
            # esse codigo adiciona o caminho_atual na saida se ele for vazio e
            # vazio estiver habilitado
            # executa apos cada termino do for interno
            # se a lista arquivos_na_pasta for vazia adiciona o caminho atual
            if inclui_subdirs:
                if relativo:
                    caminho_atual_ok = path.relpath(caminho_atual, caminho_raiz)
                else:
                    caminho_atual_ok = caminho_atual
                # ignora entrada "." e caminho_raiz
                if caminho_atual_ok != "." and caminho_atual != caminho_raiz:
                    # adiciona / no final para diretorios
                    sep = "/" if posix else path.sep
                    caminho_atual_ok += sep
                    # evita inserir duplicata
                    if caminho_atual_ok not in retorno_lista_arquivos_no_diretorio:
                        retorno_lista_arquivos_no_diretorio.append(caminho_atual_ok)
    return retorno_lista_arquivos_no_diretorio


def copia_arquivo(caminho_arquivo, destino):
    with open(caminho_arquivo, 'rb') as entrada, open(destino, 'wb') as saida:
        saida.write(entrada.read())
        if valores_globais.debug:
            print("arquivo copiado para:", destino)