from criador_json import criador_json as cj

# dicionario que configura o suporte a arquivos compactados relacionando o tipo do arquivo com o
# descompactador e o handler da listagem de arquivos. As entradas devem seguir a conveção:
# "tipo": ("metodo_extrair", "metodo_listar_conteudo"). Onde "tipo" é a extensão conhecida para o tipo de arquivo e
# metodo_extrair é o nome da função em descompactadores_utils.py que pode ser chamada para extrair arquivos desse tipo e
# metodo_listar_conteudo é o nome da função em descompactadores_utils.py que retorna a lista com os nomes de arquivos
# contidos em aruivos comprimidos desse tipo.
descompactadores_json_inicial = '{\n\
  "json_ver": 0,\n\
  ".7z": ["extrair_arquivo_7zip", "listar_conteudo_7z"],\n\
  ".zip": ["extrair_arquivo_zip", "listar_conteudo_zip"],\n\
  ".bz2": ["descompactar_bzip2", "listar_conteudo_bzip2"],\n\
  ".gz": ["descompactar_gzip", "listar_conteudo_gzip"],\n\
  ".xz": ["descompactar_xz", "listar_conteudo_xz"],\n\
  ".tar": ["descompactar_tar", "listar_conteudo_tar"],\n\
  ".tar.bz2": ["descompactar_tar_bz2", "listar_conteudo_tar_bz2"],\n\
  ".tar.gz": ["descompactar_tar_gz", "listar_conteudo_tar_gz"],\n\
  ".lzh": ["extrair_arquivo_lzh", "listar_conteudo_lzh"],\n\
  ".tar.xz": ["descompactar_tar_xz", "listar_conteudo_tar_xz"],\n\
  ".lha": ["extrair_arquivo_lzh", "listar_conteudo_lzh"],\n\
  ".pma": ["extrair_arquivo_pma", "listar_conteudo_pma"]\n\
}'
# carrega objeto dicionario a partir do arquivo "descompactadores.json" se existir se não existir cria um a partir do
# json padrão acima e carrega ele.
descompactadores = cj.carrega_ou_cria_config("descompactadores.json", descompactadores_json_inicial)
