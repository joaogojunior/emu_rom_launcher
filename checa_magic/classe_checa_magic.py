from criador_json import criador_json as cj
from binascii import hexlify

import valores_globais


# A classe ChecaMagic tem o objetivo de descobrir o tipo de um arquivo a partir de definições de strings
# com os magicbytes codificados que são fornecidas por json no formato: "string codificada": "chave" ou
# "string codificada": "chave1 chave2"
class ChecaMagic:
    def __init__(self, *magic_bytes_json_files):
        # dicionario que carregas as definições no formato "string": "chave" ou "string": "chave1 chave2"
        self.mb_tipos_dict = {}
        # seta o verbose em criador_json para o valor de debug em variaveis_globais, afim de suprimir as mensagens
        # provenientes de criador_json quando debug for False ou habilitá-las quando for True.
        cj.verbose = valores_globais.debug
        # itera na lista de json fornecida e atualiza o dicionario de definições
        # aceita um caminho para o json ou um dict ja carregado.
        for json_file in magic_bytes_json_files:
            if isinstance(json_file, str):
                self.mb_tipos_dict.update(cj.carrega_config(json_file)[0])
            elif isinstance(json_file, dict):
                self.mb_tipos_dict.update(json_file)
            else:
                print("Erro! tipo nao suportado:", type(json_file))
                exit(1)


    @staticmethod
    def __consome_fitas(fita_comparacao, bytes_restante):
        # Esse metodo utiliza o principio de um automato que deve consumir dois buffers de dados, um com a cadeia de
        # caracteres que constituem a fita de comparacao onde as regras das checagens estão armazenadas e outra com os
        # bytes proveniente do arquivo a ser investigado, se todos os bytes forem aceitos finaliza com sucesso, em
        # qualquer outro caso falha.
        # A implementaçãp consiste de um loop que a cada interação deve haver o consumo dos dois buffers que serão
        # comparados e aceitos de acordo com as regras definidas em fita_comparacao, se todos os bytes forem aceitos
        # e ambos os buffers esvaziarem simultaneamente isso significa que o tipo do arquivo pode ser confirmado e True
        # sera retornado sinalizando isso. Se em algum ponto o byte não for aceito ou se houver algum problema lógico
        # com as checagens na fita ou até mesmo outra situação não prevista de erro que leve a um loop infinito então
        # False deve ser retornado, sinalizando que a cadeia não foi aceita.

        # variavel usada para detectar loop infinito :)
        valores_ultima_iteracao = None

        # variavel index do buffer fita_comparacao
        fita_index = 0

        # variavel index do buffer bytes_restante
        restante_index = 0

        # itera até que ambos os buffers sejam totalmente checados (simultaneamente)
        # os index fita_index e restante_index vao sendo incrementados a cada iteração desse codigo, e quando eles
        # ultrapassarem o limite len(fita_comparacao) - 1 e len(bytes_restante) - 1 (que significam os valores de index
        # necessários para acessar os ultimos caracteres da fita e em bytes_restante), que por sua vez sinalizam que
        # todos os caracteres foram acessado finalizando o loop.
        while fita_index <= len(fita_comparacao) - 1 and restante_index <= len(bytes_restante) - 1:
            # checa se estamos em loop infinito e aborta com erro:
            # checamos se os valores de fita_index e restante_index alteraram desde a ultima iteracao
            if valores_ultima_iteracao != (fita_index, restante_index):
                # valores alteraram guarda estes
                valores_ultima_iteracao = (fita_index, restante_index)
            else:
                # valores permaneceram o mesmo por indução estamos num loop infinito, sai com erro:
                print("Erro: Detectado loop infinito enquanto determinava o tipo do arquivo!")
                print("verifique os dados por erros:")
                print("fita_comparacao:", fita_comparacao)
                print("bytes_restantes:", bytes_restante)
                print("fita_index:", str(fita_index))
                print("restante_index:", str(restante_index))
                exit(1)
            # checa o proximo caractere
            caractere_atual_fita = fita_comparacao[fita_index:fita_index + 1]
            byte_atual = bytes_restante[restante_index:restante_index + 1]
            match caractere_atual_fita:
                case "X":
                    # DONTCARE
                    # ex: ...X... - aceita e consome os bytes, tamanho do comando 1.
                    # consome 1 caractere da fita
                    fita_index += 1
                    # consome 1 byte de bytes_restante
                    restante_index += 1
                case "=":
                    # VALOR EXATO
                    # ex: ...=FF... - o proximo bytes tem que ser FF para ser aceito, tamanho do comando 3.
                    # compara o byte atual com dois 2 caracters hex após = em fita_comparação.
                    byte_comparacao = bytes.fromhex(fita_comparacao[fita_index + 1:fita_index + 3])
                    # checa se são iguais
                    if byte_comparacao == byte_atual:
                        # aceita e consome bytes em fita_comparação e bytes_restante
                        # consome 3 caracteres em fita comparacao
                        fita_index += 3
                        # consome 1 byte em byte_restante
                        restante_index += 1
                    else:
                        # não aceitou o byte interrompe o loop
                        break
                case _:
                    # INTERVALO VALORES VALIDOS
                    # ex: ...00BF... - compara o byte em byte_restante[:1] com o intervalo definido por 4 caracters hexa
                    # em fita_comparacao. Os dois primeiros caracteres são o valor minimo que o byte a ser testado e os
                    # dois últimos o valor máximo. Nesse exemplo o próximo byte tem que ser um valor entre 00 e BF para
                    # ser aceito. Tamanho do comando 4.
                    # os dois primeiros caracteres sao o mínimo
                    minimo = bytes.fromhex(fita_comparacao[fita_index:fita_index + 2])
                    # os ultimos dois caracteres são o valor máximo que o byte a ser testado pode assumir
                    maximo = bytes.fromhex(fita_comparacao[fita_index + 2:fita_index + 4])
                    # checa se o próximo byte está no intervalos
                    if minimo <= byte_atual <= maximo:
                        # aceita e consome byte
                        # consome 4 caracters da fita
                        fita_index += 4
                        # consome 1 byte dos bytes restantes
                        restante_index += 1
                    else:
                        # não aceitou o byte interrompe o loop
                        break
        # checa se consumiu todos os bytes corretamente ou se o loop foi interrompido prematuramente
        if len(bytes_restante) == restante_index and len(fita_comparacao) == fita_index:
            # consumiu tudo retorna o tipo detectado
            return True
        return False

    def __valida_tipo(self, magic_bytes, magic_arquivo, fita_comparacao, argumento):
        # tenta detectar o tipo comparando os magic bytes e os bytes proveniente do arquivo, opcionalmente utilizando
        # uma fita_comparação para validar bytes restantes de acordos com critérios que variar entre adminitir uma
        # faixa de valores ou um valor especifico ou então ser ignorado naquela checagem.
        # caso base: checa se o magic_bytes e magic_aruivo são iguais (caso que apenas os magic bytes são suficientes)
        # so serao iguais aqui quando "+" não esta em magic_encoded e fita_comparacao = ""
        if magic_bytes == magic_arquivo:
            # encontrou o tipo certo retorna True...
            return True
        # checa se ao menos o inicio de magic_arquivo é o composto por magic_bytes
        elif magic_bytes == magic_arquivo[:len(magic_bytes)]:
            # Ainda falta comparar os restantes dos bytes para ser aceito, vamos ter que
            # conferir todos os bytes em bytes_restante e a string em fita_comparacao.
            # checa se eh necessario ler novos magics do argumento passado
            if fita_comparacao[0] == ".":
                if valores_globais.debug:
                    print("fita comparacao antes:", fita_comparacao)
                # obten ponteiro dos ultimos dois bytes em magic_arquivo lidos e invertidos (little endian)
                # e interpletados como o offset no arquivo onde tera que adquirir ate mais 9
                # bytes sinalizados pelo inteiro decimal de 1 digito apos o ponto
                offset_pointer = (magic_arquivo[-1] << 8) | magic_arquivo[-2]
                qtd = int(fita_comparacao[1])
                bytes_restante = self.obtem_magic_arquivo(argumento, offset_pointer, qtd)
                # consome a fita em dois caracteres
                fita_comparacao = fita_comparacao[2:]
                if valores_globais.debug:
                    print("magic arquivo:", magic_arquivo)
                    print("offset ponteiro ->", offset_pointer)
                    print("qtd de bytes a ler ->", qtd)
                    print("novo bytes_restante :", bytes_restante)
                    print("fita comparacao depois:", fita_comparacao)
            else:
                index_minus_fita = fita_comparacao.find("-")
                fita_comparacao = fita_comparacao[index_minus_fita + 1:]
                # bytes_restante são os bytes ainda não validados provenientes do arquivo
                bytes_restante = magic_arquivo[len(magic_bytes):]
                if valores_globais.debug:
                    print("magic_arquivo:", magic_arquivo)
                    print("fita que chegou aqui:", fita_comparacao)
                    print("fita final:", fita_comparacao)
                    print("magic_arquivo:", magic_arquivo)
                    print("bytes_restante:", bytes_restante)
            # usa o automato em __consome_fitas para validar o buffer bytes_restante utilizando fita_comparacao
            if self.__consome_fitas(fita_comparacao, bytes_restante):
                # Como __consome_fitas aceitou bytes_restante, o tipo atual é válido. Retorna True.
                return True
        # para todos os outros casos (magic_bytes nao esta presente em magic_arquivo ou __consome_fitas nao validou o
        # tipo):
        return False

    @staticmethod
    def __le_bytes_file_handler(file_handler, offset_magic_bytes, tam_magic_bytes):
        # faz leitura dos bytes do arquivo no offset calculado
        try:
            # ajusta a leitura do arquivo no offset certo
            file_handler.seek(offset_magic_bytes)
            # le a quantidade de bytes calculada em tam_magic_bytes do arquivo
            magic_arquivo = file_handler.read(tam_magic_bytes)
            if valores_globais.debug:
                print("raw magic do arquivo:", hexlify(magic_arquivo).decode('utf-8').upper())
        except IOError as e:
            # aborta se a leitura falhar...
            print("Erro lendo arquivo, abortando...", str(e))
            exit(1)
        return magic_arquivo

    @staticmethod
    def __converte_magic_encoded(magic_encoded):
        # magic_encoded tem quer ser convertido em offset, bytes e opcionalmente uma fita de comparação.
        # o offset são os 6 primeiros caracteres de magic_bytes em hexa o que permite um offset de ate FFFFFF (16M)
        # converte uma string de 6 caracteres em hexadecimal em um valor int
        offset_magic_bytes = int(magic_encoded[:6], 16)
        # fita_comparacao inicial
        fita_comparacao = ""
        # marcador operacao de leitura adicional de bytes
        index_mais = magic_encoded.find("+")
        # marcador operacao de avanço de bytes
        index_maiorque = magic_encoded.find(">")
        # marcador operacao le pointer
        index_ponto = magic_encoded.find(".")
        # testa se nao existe ">", "+" ou "." na string, o valor -1 significa que nao foi encontrado
        if index_mais == -1 and index_maiorque == -1 and index_ponto == -1:
            # string de magic_bytes apenas
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
            return fita_comparacao, magic_bytes, offset_magic_bytes, tam_magic_bytes
        # prepara as variaveis de retorno para a proxima etapa no caso de "." ou "+"
        (index_fatia, index_fim_op, tam_operacao) =\
            (index_ponto, index_ponto + 1, int(magic_encoded[index_ponto + 1:index_ponto + 2]))\
            if (index_ponto != -1) else \
            (index_mais, magic_encoded.find("-"), int(magic_encoded[index_mais + 1:magic_encoded.find("-")]))
        if index_maiorque > -1:
            # string de magic bytes encoded possui um avanco de n bytes representado
            # pelo decimal entre dois ">", cono por exemplor: ">2>" significando avanca
            # dois bytes para que dai seja lido mais bytes com a fita de comparacao.
            # Ex: compara o primeiro bytem com "T" avanca 4, nessa posicão le mais um byte
            # e o compara com "E", se comparado com a strint de bytes b"TESTE"
            # EX2: 00000054>4+1-=45
            index_fim_mq = magic_encoded.find(">", index_maiorque + 1)
            tam_mb_fixo = len(magic_encoded[6:index_maiorque]) // 2
            tam_mb_ignorar = int(magic_encoded[index_maiorque + 1: index_fim_mq])
            magic_bytes = bytes.fromhex(magic_encoded[6:index_maiorque])
            if index_mais > -1:
                # na operacao "+" em conjunto com ">" ja carrega o buffer com todos
                # os bytes inclusive o da comparacao entao ja soma tan_seguinte aqui
                tam_magic_bytes = tam_mb_fixo + tam_mb_ignorar + tam_operacao
                # adicionar caracteres dont care na quantidade dos bytes a ignorar
                fita_comparacao = ("+" + str(tam_operacao + tam_mb_ignorar) + "-" +
                                   "X" * tam_mb_ignorar + magic_encoded[index_fim_op + 1:])
            else:
                # na operacao "." o buffer nao tem os bytes da comparacao pq eles so serao
                # encontrados apos o ponteiro ser intepretado, o buffer contem nas ultimas duas
                # posicoes o ponteiro a ser lido para carregamento posterior dos bytes da comparacao
                tam_magic_bytes = tam_mb_fixo + tam_mb_ignorar
                fita_comparacao = (magic_encoded[index_fim_mq + 1:])
            if valores_globais.debug:
                print("magic_encoded:", magic_encoded)
                print("tam_mb_fixo:", tam_mb_fixo)
                print("tam_mb_ignorar:", tam_mb_ignorar)
                print("magic_bytes:", magic_bytes)
                print("fita_comparacao:", fita_comparacao)
        else:
            # a string magic_encoded nao possuia operacao ">" entao incializa
            # as variaveis de retorno para proxima etapa
            # tamanho dos magic bytes fixos
            tam_mb_fixo = len(magic_encoded[6:index_fatia]) // 2
            tam_magic_bytes = tam_mb_fixo + tam_operacao
            # os primeiros 6 caracteres hexa de magic_encoded sao o offset
            # apos inicia os magic bytes e possivel fica te comparacao
            magic_bytes = bytes.fromhex(magic_encoded[6:index_fatia])
            # fita inclui a operacao
            fita_comparacao = magic_encoded[index_fatia:]
        return fita_comparacao, magic_bytes, offset_magic_bytes, tam_magic_bytes

    def obtem_magic_arquivo(self, argumento, offset_magic_bytes, tam_magic_bytes):
        if valores_globais.debug:
            print("Obtendo magic a partir de argumento...")
            print("offset_magic_bytes:", offset_magic_bytes)
            print("tam_magic_bytes:", tam_magic_bytes)
        # checa oo tipo de argumento
        match str(type(argumento)):
            case "<class 'bytes'>":
                if valores_globais.debug:
                    print("tipo de argumento: buffer (bytes)")
                # bytes_arquivo
                # obtem bytes do arquivo a partir de uma fatia do buffer fornecido
                return argumento[offset_magic_bytes: offset_magic_bytes + tam_magic_bytes]
            case "<class 'str'>":
                if valores_globais.debug:
                    print("tipo de argumento: caminho do arquivo (str)")
                # abre argumento como caminho_arquivo
                try:
                    with open(argumento, 'rb') as arquivo_handler:
                        # se abrir com sucesso tenta obter dados do arquivo utilizando __le_bytes_file_handler()
                        return self.__le_bytes_file_handler(
                            arquivo_handler, offset_magic_bytes, tam_magic_bytes)
                except PermissionError:
                    return b"Erro: Acesso negado."
                except FileNotFoundError:
                    return b"Erro: Arquivo nao encontrado."
            case _:
                if valores_globais.debug:
                    print("tipo de argumento: objeto tipo", str(type(argumento)))
                # considera argumento um objeto compativel com _io.BufferedReader
                # obtem bytes a partir de __le_bytes_file_handler()
                return self.__le_bytes_file_handler(argumento, offset_magic_bytes, tam_magic_bytes)

    def detecta_tipo(self, argumento):
        # cache de magic_bytes lidos do arquivo contendo até os 10 primeiros bytes do arquivo
        magic_bytes_cache = ""
        # Itera em todos os items em (chaves e valores) no dicinario magic_bytes_tipos
        # esse for testa cada tipo possivel para o arquivo em file_handler um por vez processando magic_encoded e
        # comparando com a sequencia de bytes de tamanho variavel lidos de lugares e tamanhos definidos em
        # magic_encoded.
        for magic_encoded, tipo in self.mb_tipos_dict.items():
            # processa magic_encoded
            fita_comparacao, magic_bytes, offset_magic_bytes, tam_magic_bytes = (
                self.__converte_magic_encoded(magic_encoded))
            # se o cache ja tiver populado verifica se tem o que procura
            if offset_magic_bytes == 0 and tam_magic_bytes < len(magic_bytes_cache):
                if valores_globais.debug:
                    print("o cache possui os dados de magic suficientes.")
                magic_arquivo = magic_bytes_cache[:tam_magic_bytes]
            else:
                magic_arquivo = self.obtem_magic_arquivo(argumento, offset_magic_bytes, tam_magic_bytes)
                # checa se a string "Erro:" existe logo no seu inicio, indicando erro.
                if magic_arquivo[:5] == b"Erro:":
                    if valores_globais.debug:
                        print("Detectado erro ao obter magic do arquivo...")
                    return "Desconhecido", magic_arquivo

            # verifica se deve atualizar magic_bytes_cache aproveitando os dados lidos. Se o offset for zero e se o
            # tamanho desse magic lido for maior do que o tamanho do valor em magic_bytes_cache ate num tamanho maximo
            # de 10 entao atualiza o cache.
            if (offset_magic_bytes == 0 and len(magic_bytes_cache) < 10 and
                    tam_magic_bytes > len(magic_bytes_cache)):
                if valores_globais.debug:
                    print("valor lido é offset 0 e tem tamanho maior que o valor no cache...")
                if tam_magic_bytes >= 10:
                    # guarda uma amostra de magic para retornar no caso "Desconhecido" de tamanho 10 bytes
                    magic_bytes_cache = magic_arquivo[:10]
                    if valores_globais.debug:
                        print("atualizando cache com amostra dos 10 primeiros bytes")
                else:
                    # o tamanho for menor que 10 guarda tudo
                    magic_bytes_cache = magic_arquivo[:]
                    if valores_globais.debug:
                        print("atualizando cache com amostra tamanho", len(magic_arquivo))
            # valida se esse tipo é o certo
            if self.__valida_tipo(magic_bytes, magic_arquivo, fita_comparacao, argumento):
                if valores_globais.debug:
                    print("validado para o tipo atual, retornando %s e %s:" %(tipo, magic_encoded))
                return tipo, magic_encoded
        if valores_globais.debug:
            print("não aceitou esse tipo, retornando 'Desconhecido' e", magic_bytes_cache)
        # retorna tipo não detectado
        # retorna uma amostra do magic do arquivo de ate 10 bytes se houver no cache...
        return 'Desconhecido', magic_bytes_cache
