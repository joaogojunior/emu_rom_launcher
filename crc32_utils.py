import zlib


# calcula crc32 a partir de uma string com o caminho do arquivo
def calcular_crc32_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as arquivo_handler:
        return calcular_crc32_file_handle(arquivo_handler)


# calcula crc32 a partir de manipulador de arquivos
def calcular_crc32_file_handle(arquivo_handler):
    # Leitura em blocos para arquivos grande (le arquivo em blocos de 4k para ser melhor com o consumo de ram)
    crc32 = 0
    for bloco in iter(lambda: arquivo_handler.read(4096), b''):
        crc32 = zlib.crc32(bloco, crc32)
    # Ajusta para um valor não assinado de 32 bits
    return crc32 & 0xFFFFFFFF


# calcula crc32 em um único passo, requer que o conteudo inteiro esteja carregado
def calcular_crc32_bytes(conteudo_arquivo_bytes):
    crc32 = zlib.crc32(conteudo_arquivo_bytes, 0)
    return crc32 & 0xFFFFFFFF
