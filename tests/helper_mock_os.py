# import os.path
import sys

import pytest
import io
from os import path as os_path
from collections import defaultdict

import valores_globais

open_b_mode = False

# fake open classe de suporte
class StrictBytesIO(io.BytesIO):
    def write(self, b: bytes| str):
        if not isinstance(b, (bytes, bytearray)):
            if valores_globais.debug:
                print(f"Esperado bytes, mas recebeu {type(b).__name__}, encodando como utf-8")
            b = b.encode("utf-8")
        if valores_globais.debug:
            print("escrevendo bytes:", b)
        return super().write(b)

    def close(self):
        # Impede fechamento automático para inspeção
        pass

    def read(self, s:int | None = -1):
        b: bytes = super().read(s)
        if valores_globais.debug:
            print("lendo %s bytes: %s" %(s,b))
        if open_b_mode:
            return b
        else:
            return b.decode("utf-8")

    def reset(self):
        self.seek(0)


# mocker do open
@pytest.fixture
def mocker_open(monkeypatch):
    arquivos = {}
    # mode = 'r',
    def fake_open(caminho, mode, buffering = -1, encoding = 'utf-8', errors = None, newline = None):
        global open_b_mode
        if "b" not in mode:
            open_b_mode = False
            # raise ValueError(f"Somente modos binários são suportados ('rb', 'wb', 'ab'). Recebido: '{modo}'")
        else:
            open_b_mode = True

        if "r" in mode:
            # se nao existir
            if caminho not in arquivos:
                raise FileNotFoundError(f"Arquivo {caminho} não foi criado.")
            # se for diretorio (diretorio tem None como dado e nao um buffer)
            elif arquivos[caminho] is None:
                raise PermissionError("nao pode acessar diretirios diretamente com open...")
            buffer = arquivos[caminho]
            if valores_globais.debug:
                print("reading from buffer...", buffer)
            buffer.reset()
            return buffer
        elif "w" in mode:
            if caminho in arquivos and arquivos[caminho] is None:
                raise IsADirectoryError("nao pode sobrescrever diretorios com open...")
            buffer = StrictBytesIO()
            arquivos[caminho] = buffer
            if valores_globais.debug:
                print("writing (or creating) buffer...", buffer)
            return buffer
        elif "a" in mode:
            if caminho in arquivos and arquivos[caminho] is None:
                raise IsADirectoryError("nao pode sobrescrever diretorios com open...")
            buffer = arquivos.get(caminho, None)
            if valores_globais.debug:
                print("trying to read buffer in append, got:", buffer)
            # para arquivos recem criados atualiza arquivos[caminho]
            if not buffer:
                buffer = StrictBytesIO()
                arquivos[caminho] = buffer
                if valores_globais.debug:
                    print("creating new buffer in append...", buffer)
            # posiciona o buffer no fim do arquivo
            buffer.seek(0, io.SEEK_END)
            return buffer
        return None

    monkeypatch.setattr("builtins.open", fake_open)
    monkeypatch.setattr("io.open", fake_open)
    return arquivos

class FakeOs:
    _mocker_open = None

    def __init__(self, _mocker_open):
        self._mocker_open = _mocker_open

    def walk(self, top, _topdown=True, **kwargs):
        # Normaliza o caminho de entrada
        top = os_path.normpath(top)

        # Mapeamos o que existe em cada nível
        pastas_por_nivel = defaultdict(set)
        arquivos_por_nivel = defaultdict(set)

        for caminho_completo in self._mocker_open.keys():
            if caminho_completo.startswith(top):
                # Extrai a parte relativa ao 'top' para processar os níveis
                pasta_pai, nome = os_path.split(caminho_completo)
                arquivos_por_nivel[pasta_pai].add(nome)

                # Sobe a árvore para registrar as pastas intermediárias
                atual = pasta_pai
                while atual != top and atual != "/":
                    pai, filho = os_path.split(atual)
                    pastas_por_nivel[pai].add(filho)
                    atual = pai

        # Simula a iteração do walk (apenas para as pastas que descobrimos)
        diretorios_para_visitar = [top]
        while diretorios_para_visitar:
            atual = diretorios_para_visitar.pop(0)
            list_pastas = sorted(list(pastas_por_nivel[atual]))
            list_arquivos = sorted(list(arquivos_por_nivel[atual]))

            yield atual, list_pastas, list_arquivos

            # Adiciona subpastas na fila para continuar o walk
            diretorios_para_visitar.extend([os_path.join(atual, p) for p in list_pastas])

    def rename(self, _src, _dst):
        # print("debug:", self._mocker_open.keys())
        if sys.platform == "win32":
            src = _src.replace("/", "\\")
        else:
            src = _src.replace("\\", "/")
        if src in self._mocker_open.keys():
            buffer = self._mocker_open[src]
            del self._mocker_open[src]
            self._mocker_open[_dst] = buffer
        else:
            raise FileNotFoundError("Não foi possivel encontrar o arquivo %s. %s" %(_src, list(self._mocker_open.keys())))

    def makedirs(self, _caminho: str, exist_ok: bool = True):
        # checa se caminho tem / no final
        if _caminho[-1] != os_path.sep:
            _caminho += os_path.sep
        # checa o que faz se ja existir o arquivo criado
        if _caminho in self._mocker_open.keys():
            # checa se eh arquivo regular ou se _exists_ok é falso
            if self._mocker_open[_caminho] is not None or not exist_ok:
                raise FileExistsError("arquivo %s ja existe e nao pode ser sobreescrito." % _caminho)
        # se _caminho nao existia previamente ou se existia como diretorio e _exist_ok é verdadeiro
        # entao cria o diretorio:
        self._mocker_open[_caminho] = None

    @staticmethod
    def utime(_caminho, **kwargs):
        if valores_globais.debug:
            print("times:", kwargs["times"])
        # vou tentar nao fazer nada e ver no que da
        pass


# mock do os_path
class FakeOsPath:
    _mocker_open = None

    def __init__(self, _mocker_open):
        self._mocker_open = _mocker_open

    @staticmethod
    def split(_filename):
        return os_path.split(_filename)

    def isfile(self, _arquivo):
        # simula o retorno correto para arquivos que foram criado no mock anteriormente
        if _arquivo in self._mocker_open.keys():
            return True
        return False

    def isdir(self, _dir):
        if self.isfile(_dir) and self._mocker_open[_dir] is None:
            return True
        else:
            return False

    @staticmethod
    def join(par1, par2):
        return os_path.join(par1, par2)

# close dos arquivos no buffer
def close_all(mocker):
    for buffer in mocker.values():
        if buffer:
            super(StrictBytesIO, buffer).close()

# fabrica de interceptadores
def criar_interceptador_self_kwargs(metodo_customizado):
    """
    Cria uma função compatível com patch(autospec=True) que
    redireciona a chamada para um metodo customizado
    fora da classe em tempo de execução para fins de
    teste. capturando o parametro self (referencia ao
    objeto original) junco com outros parametros (kwargs)
    e repassando ao metodo_customizado.
    """

    def interceptador(self_instancia, *args, **kwargs):
        # Repassa para o metodo pre-configurado
        return metodo_customizado(self_instancia, **kwargs)

    return interceptador
