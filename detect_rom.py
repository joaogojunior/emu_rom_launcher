from criador_json import criador_json as cj
from binascii import hexlify
from sys import argv, exit
from os import path, listdir
from pyinstaller_build_date import data_hora_build

# debug prints
debug = False


class DetectMagicBytes:
    def __init__(self, *magic_bytes_json_files):
        self.mb_tipos_dict = {}
        for json_file in magic_bytes_json_files:
            self.mb_tipos_dict.update(cj.carrega_config(json_file)[0])

    @staticmethod
    def consome_fitas(fita_comparacao, bytes_restante):
        # variavel usada para detectar loop infinito :)
        valores_ultima_iteracao = None
        while len(fita_comparacao) > 0 and len(bytes_restante) > 0:
            # checa se estamos em loop infinito e aborta com erro:
            # checamos se os valores de fita_comparacao e bytes_restante alteraram desde a ultima iteracao
            if valores_ultima_iteracao != (fita_comparacao, bytes_restante):
                # valores alteraram guarda estes
                valores_ultima_iteracao = (fita_comparacao, bytes_restante)
            else:
                # valores permaneceram o mesmo por indução estamos num loop infinito, sai com erro:
                print("Erro: Detectado loop infinito enquanto determinava o tipo do arquivo!")
                print("verifique a fita_comparacao por erros:", fita_comparacao)
                exit(1)
            # checa se o proximo caractere da fita é X
            if fita_comparacao[:1] == "X":
                # ex: ...X... - dont care aceita o proximo byte em byte_restante[c], tamanho do comando 1.
                # consome 1 caractere da fita
                fita_comparacao = fita_comparacao[1:]
                # consome 1 byte de bytes_restante
                bytes_restante = bytes_restante[1:]
            elif fita_comparacao[:1] == "=":
                # ex: ...=FF... - o proximo bytes tem que ser FF para ser aceito, tamanho do comando 3.
                # compara o byte em byte_restante[:1] com dois 2 caracters hex após = em fita_comparação.
                byte_comparacao = bytes.fromhex(fita_comparacao[1:3])
                # checa se são iguais
                if byte_comparacao == bytes_restante[:1]:
                    # aceita e consome bytes em fita_comparação e bytes_restante
                    # consome 3 caracteres em fita comparacao
                    fita_comparacao = fita_comparacao[3:]
                    # consome 1 byte em byte_restante
                    bytes_restante = bytes_restante[1:]
                else:
                    # não aceitou o byte interrompe o loop
                    break
            else:
                # ex: ...00BF... - compara o byte em byte_restante[:1] com o intervalo definido por 4 caracters hexa
                # em fita_comparacao. Os dois primeiros caracteres são o valor minimo que o byte a ser testado e os
                # dois últimos o valor máximo. Nesse exemplo o próximo byte tem que ser um valor entre 00 e BF para
                # ser aceito. Tamanho do comando 4.
                # os dois primeiros caracteres sao o mínimo
                minimo = bytes.fromhex(fita_comparacao[:2])
                # os ultimos dois caracteres são o valor máximo que o byte a ser testado pode assumir
                maximo = bytes.fromhex(fita_comparacao[2:4])
                # checa se o próximo byte em byte_restante[:1] está no intervalos
                if minimo <= bytes_restante[:1] <= maximo:
                    # aceita e consome byte
                    # consome 4 caracters da fita
                    fita_comparacao = fita_comparacao[4:]
                    # consome 1 byte dos bytes restantes
                    bytes_restante = bytes_restante[1:]
                else:
                    # não aceitou o byte interrompe o loop
                    break
        # checa se consumiu todos os bytes corretamente ou se o loop foi interrompido prematuramente
        if len(bytes_restante) == 0 and len(fita_comparacao) == 0:
            # consumiu tudo retorna o tipo detectado
            return True
        return False

    def valida_tipo(self, magic_bytes, magic_arquivo, fita_comparacao):
        # tenta detectar o tipo comparando os magic bytes lidos do offset calculado
        # checa se o magic_bytes e magic_aruivo são iguais
        # so serao iguais aqui quando "+" não esta em magic_encoded
        if magic_bytes == magic_arquivo:
            # encontrou o tipo certo retorna ele...
            return True
        # checa se o inicio de magic_arquivo é o composto por magic_bytes
        elif magic_bytes == magic_arquivo[:len(magic_bytes)]:
            # ainda faltam comparar os restantes dos bytes, para ser aceito, temos que consumir todos os bytes em
            # bytes_restante e a string em fita_comparacao.
            # bytes_restante são os bytes ainda não validados do arquivo
            bytes_restante = magic_arquivo[len(magic_bytes):]
            # testa se consume fita_comparacao e bytes_restante corretamente
            if self.consome_fitas(fita_comparacao, bytes_restante):
                return True
        return False

    def detecta_tipo_bytes(self, bytes_arquivo):
        # magic bytes que vai ser retornado caso nao detecte o tipo, esse valor vai ser atualizado assim que for
        # encontrado uma string maior de offset 0
        magic_bytes_nao_detectado = ""
        # Itera em todos os items em (chaves e valores) no dicinario magic_bytes_tipos
        # esse for testa cada tipo possivel para o arquivo em file_handler um por vez processando magic_encoded e
        # comparando com a sequencia de bytes de tamanho variavel lidos de lugares e tamanhos definidos em
        # magic_encoded.
        for magic_encoded, tipo in self.mb_tipos_dict.items():
            # processa magic_encoded
            fita_comparacao, magic_bytes, offset_magic_bytes, tam_magic_bytes = (
                self.converte_magic_encoded(magic_encoded))
            # se o cache ja tiver populado verifica se tem o que procura
            if offset_magic_bytes == 0 and tam_magic_bytes < len(magic_bytes_nao_detectado):
                magic_arquivo = magic_bytes_nao_detectado[:tam_magic_bytes]
            else:
                # obtem bytes a partir dos bytes do arquivo
                magic_arquivo = bytes_arquivo[offset_magic_bytes: offset_magic_bytes + tam_magic_bytes]
            # verifica se o offset é zero e se o tamanho desse magic é maior do que o valor em magic_bytes_nao_detectado
            if (offset_magic_bytes == 0 and len(magic_bytes_nao_detectado) < 10 and
                    tam_magic_bytes > len(magic_bytes_nao_detectado)):
                if tam_magic_bytes >= 10:
                    # guarda uma copia do magic para retornar no caso "Desconhecido" de tamanho ate 10 bytes
                    magic_bytes_nao_detectado = magic_arquivo[:10]
                else:
                    # o tamanho eh menor que 10 guarda tudo
                    magic_bytes_nao_detectado = magic_arquivo
            # valida se esse tipo é o certo
            if self.valida_tipo(magic_bytes, magic_arquivo, fita_comparacao):
                return tipo, magic_encoded
        # retorna tipo não detectado
        # print("tipo não determinado para os bytes fornecidos:", magic_bytes_nao_detectado)
        return 'Desconhecido', magic_bytes_nao_detectado

    def detecta_tipo_file_handler(self, file_handler):
        # magic bytes que vai ser retornado caso nao detecte o tipo, esse valor vai ser atualizado assim que for
        # encontrado uma string maior de offset 0
        magic_bytes_nao_detectado = ""
        # Itera em todos os items em (chaves e valores) no dicinario magic_bytes_tipos
        # esse for testa cada tipo possivel para o arquivo em file_handler um por vez processando magic_encoded e
        # comparando com a sequencia de bytes de tamanho variavel lidos de lugares e tamanhos definidos em
        # magic_encoded.
        for magic_encoded, tipo in self.mb_tipos_dict.items():
            # processa magic_encoded
            fita_comparacao, magic_bytes, offset_magic_bytes, tam_magic_bytes = (
                self.converte_magic_encoded(magic_encoded))
            # obtem bytes do arquivo
            magic_arquivo = self.le_bytes_file_handler(file_handler, offset_magic_bytes, tam_magic_bytes)
            # verifica se o offset é zero e se o tamanho desse magic é maior do que o valor em magic_bytes_nao_detectado
            if offset_magic_bytes == 0 and 8 >= tam_magic_bytes > len(magic_bytes_nao_detectado):
                # guarda uma copia do magic para retornar no caso "Desconhecido"
                magic_bytes_nao_detectado = magic_arquivo
            # valida se esse tipo é o certo
            if self.valida_tipo(magic_bytes, magic_arquivo, fita_comparacao):
                return tipo, magic_encoded
        # retorna tipo não detectado
        # print("tipo não determinado processando file handler: %s" % magic_bytes_nao_detectado)
        return 'Desconhecido', magic_bytes_nao_detectado

    @staticmethod
    def le_bytes_file_handler(file_handler, offset_magic_bytes, tam_magic_bytes):
        # faz leitura dos bytes do arquivo no offset calculado
        try:
            # ajusta a leitura do arquivo no offset certo
            file_handler.seek(offset_magic_bytes)
            # le a quantidade de bytes calculada em tam_magic_bytes do arquivo
            magic_arquivo = file_handler.read(tam_magic_bytes)
            if debug:
                print("raw magic do arquivo:", hexlify(magic_arquivo).decode('utf-8').upper())
        except IOError as e:
            # aborta se a leitura falhar...
            print("Erro lendo arquivo, abortando...", str(e))
            exit(1)
        return magic_arquivo

    @staticmethod
    def converte_magic_encoded(magic_encoded):
        # magic_encoded tem quer ser convertido em offset, bytes e opcionalmente uma fita de comparação.
        # o offset são os 6 primeiros caracteres de magic_bytes em hexa o que permite um offset de ate FFFFFF (16M)
        # converte uma string de 6 caracteres em hexadecimal em um valor int
        offset_magic_bytes = int(magic_encoded[:6], 16)
        index = magic_encoded.find("+")
        match index:
            case -1:
                # ex: 000000FE - byte no offset 000000 tem que ser FE.
                # magic_encoded é composto de 6 caracteres hexa como offset e mais n caracteres hexa que serao
                # convertidos em bytes (little endian) aos pares.
                # nao tem + nesse caso o resto da string contém os bytes que terão de ser encontrados no offset.
                # tamanho magic bytes é o tamanho do resto da string dividido por 2 (como os caracteres sao hexa
                # precisam de dois para representar um byte) o primeiro hexa é o mais significativo.
                # quantidade de bytes a serem lidos para detecção
                tam_magic_bytes = len(magic_encoded[6:]) // 2
                # magic_bytes é a string de bytes obtida da fatia de magic_encoded após o sexto caractere ate o fim e
                # interpretada como valores hexadecimal. Estes são os valores deverão ser encontrados no offset
                # calculado (mais abaixo).
                magic_bytes = bytes.fromhex(magic_encoded[6:])
                # inicializa fita vazia
                fita_comparacao = ""
            case _:
                # Ex: 000000FE+3-X=004488, espera FE no offset 000000, os proximos tres bytes serao validados pela
                # fita_comparacao "X=004488", que significa que o primeiro byte pode assumir qualquer valor (X), o
                # segundo deve ser igual a 0x00 (=00) e o terceiro pode assumir qualquer valor entre 0x44 e 0x88 (4488).
                # extrai o inteiro entre os caracteres + e -, este int é a quantidade de bytes adicionais que será lida
                # do arquivo.
                # ja temos o index de "+" agora obtemos o index de "-" em index2
                index2 = magic_encoded.find("-")
                # tam_mb_antes guarda a quantidade de caracteres hexa representados antes do + em magic_encoded,
                # esses bytes opcionais serão utilizado na comparação com o bytes a serem lidos do offset calculado
                # (mais abaixo).
                tam_mb_antes = len(magic_encoded[6:index]) // 2
                # tam_mb_depois define a quantidade de bytes adicionais a serem lidos do arquivo para serem comparados
                # com as regras na fita de comparacao.
                tam_mb_depois = int(magic_encoded[index + 1: index2])
                # quantidade total de bytes a serem lidos do arquivo
                tam_magic_bytes = tam_mb_antes + tam_mb_depois
                # extrai fatia entre o setimo caractere e o + em string de bytes dos valores hexadecimais
                magic_bytes = bytes.fromhex(magic_encoded[6:index])
                # fita_comparacao é uma string com caracteres de comandos e valores hexa que serão usados na validação
                # dos bytes restantes.
                # obtem a fita a partir de magic_encoded fatiando depois do - ate o fim da string.
                fita_comparacao = magic_encoded[index2 + 1:]
        return fita_comparacao, magic_bytes, offset_magic_bytes, tam_magic_bytes

    def detecta_tipo_arquivo(self, caminho_arquivo_str):
        # abre caminho_arquivo como arquivo
        try:
            with open(caminho_arquivo_str, 'rb') as arquivo_handler:
                return self.detecta_tipo_file_handler(arquivo_handler)
        except PermissionError:
            return "Desconhecido", b"Erro: Acesso negado."


if __name__ == '__main__':
    print("detect_rom v0.1 by joaogojunior@hotmail.com lançado em:", data_hora_build)
    if len(argv) == 1:
        print("Erro! Forneca o caminho de um arquivo como parametro.")
        exit(1)
    else:
        # inicializa variaveis de controle
        ext = ""
        caminho = ""
        # procura se tem * na string argv[1] tipo c:\dir\*.bla
        fim_str_dir_index = argv[1].find("*")
        if fim_str_dir_index != -1:
            if argv[1][fim_str_dir_index + 1] != ".":
                print("Erro: extensão inválida.")
                exit(1)
            # se tiver faz ext a fatia da str apos "*."
            ext = argv[1][fim_str_dir_index + 2:]
            # caminho é a fatia antes de *
            caminho = argv[1][:fim_str_dir_index]
        else:
            # argv[1] deve ser um caminho apenas ou caminho com arquivo
            caminho = argv[1]
        print(caminho)
        # se caminho for vazio faz "."
        if caminho == "":
            caminho = "."
        # checa se caminho existe
        if not path.exists(caminho):
            # caminho nao existe..
            print("Erro! Caminho não encontrado.")
            exit(1)
        # caminho existe...
        # instancia detector de roms
        detetor = DetectMagicBytes("conf/arcs_mb.json", "conf/roms_mb.json")
        if path.isfile(caminho):
            # caminho tem um arquivo tipo c:\diretorio\arquivo.bla
            print("tipo detectado:", detetor.detecta_tipo_arquivo(caminho))
        else:
            # é um diretorio apenas
            lista_resultados = list()
            lista_arquivos = listdir(caminho)
            contador = 0
            for nome_arquivo in lista_arquivos:
                # adiciona resultado de todos os arquivos caso ext="" ou apenas os que tem extensao especificada em ext
                if ext == "" or (ext != "" and path.splitext(nome_arquivo)[1][1:].lower() == ext.lower()):
                    caminho_arquivo = path.join(caminho, nome_arquivo)
                    t, mb = detetor.detecta_tipo_arquivo(caminho_arquivo)
                    if t == "Desconhecido":
                        lista_resultados.append((nome_arquivo, mb))
                    else:
                        contador += 1
                    if debug:
                        print("tipo detectado:", nome_arquivo, t)
            for item in lista_resultados:
                print(item)
            print("%d arquivos conhecidos:" % contador)
            print("%d arquivos desconhecidos:" % len(lista_resultados))
