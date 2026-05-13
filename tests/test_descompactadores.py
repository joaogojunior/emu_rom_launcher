# usa base64 para simular os arquivos compactados
import base64
import tempfile

from tests.helper_mock_os import mocker_open, close_all, FakeOs, criar_interceptador_self_kwargs


def test_mocker_open(mocker_open):
    with open("teste.txt", "w") as arquivo:
        arquivo.write("teste123")
    close_all(mocker_open)
    #testa que o arquivo foi criado
    assert list(mocker_open.keys()) == ['teste.txt']

#  tests suporte zip
mock_archive_files_list = ['mock_archive_files/', 'mock_archive_files/file1.rom', 'mock_archive_files/file2.bin',
                               'mock_archive_files/readme.txt', 'mock_archive_files/folder/',
                               'mock_archive_files/folder/file3.png', 'mock_archive_files/empty_folder/']

extracted_archive_file_list = ['arquivo\\mock_archive_files\\', 'arquivo\\mock_archive_files\\file1.rom',
                               'arquivo\\mock_archive_files\\file2.bin', 'arquivo\\mock_archive_files\\readme.txt',
                               'arquivo\\mock_archive_files\\folder\\',
                               'arquivo\\mock_archive_files\\folder\\file3.png',
                               'arquivo\\mock_archive_files\\empty_folder\\']

mock_zip_content_base64 = (b'UEsDBAoAAAAAAClxPlwAAAAAAAAAAAAAAAATABwAbW9ja19hcmNoaXZlX2ZpbGVzL1VUCQADveV8ab3lfGl1eAsAAQ'
                           b'QAAAAABAAAAABQSwMECgAAAAAAPYs9XAAAAAAAAAAAAAAAACAAHABtb2NrX2FyY2hpdmVfZmlsZXMvZW1wdHlfZm9s'
                           b'ZGVyL1VUCQADVcJ7aVXCe2l1eAsAAQQAAAAABAAAAABQSwMECgACAAAAeXE+XAVIGGkGAAAABgAAABwAHABtb2NrX2'
                           b'FyY2hpdmVfZmlsZXMvZmlsZTEucm9tVVQJAANV5nxpVeZ8aXV4CwABBAAAAAAEAAAAAFRFU1RFClBLAwQKAAIAAAB7'
                           b'cT5cBUgYaQYAAAAGAAAAHAAcAG1vY2tfYXJjaGl2ZV9maWxlcy9maWxlMi5iaW5VVAkAA1nmfGlZ5nxpdXgLAAEEAA'
                           b'AAAAQAAAAAVEVTVEUKUEsDBAoAAAAAAFZxPlwAAAAAAAAAAAAAAAAaABwAbW9ja19hcmNoaXZlX2ZpbGVzL2ZvbGRl'
                           b'ci9VVAkAAxPmfGkT5nxpdXgLAAEEAAAAAAQAAAAAUEsDBAoAAgAAAIZxPlwFSBhpBgAAAAYAAAAjABwAbW9ja19hcm'
                           b'NoaXZlX2ZpbGVzL2ZvbGRlci9maWxlMy5wbmdVVAkAA2vmfGlr5nxpdXgLAAEEAAAAAAQAAAAAVEVTVEUKUEsDBAoA'
                           b'AgAAAJZxPlwFSBhpBgAAAAYAAAAdABwAbW9ja19hcmNoaXZlX2ZpbGVzL3JlYWRtZS50eHRVVAkAA4vmfGmL5nxpdX'
                           b'gLAAEEAAAAAAQAAAAAVEVTVEUKUEsBAh4DCgAAAAAAKXE+XAAAAAAAAAAAAAAAABMAGAAAAAAAAAAQAP9BAAAAAG1v'
                           b'Y2tfYXJjaGl2ZV9maWxlcy9VVAUAA73lfGl1eAsAAQQAAAAABAAAAABQSwECHgMKAAAAAAA9iz1cAAAAAAAAAAAAAA'
                           b'AAIAAYAAAAAAAAABAA/0FNAAAAbW9ja19hcmNoaXZlX2ZpbGVzL2VtcHR5X2ZvbGRlci9VVAUAA1XCe2l1eAsAAQQA'
                           b'AAAABAAAAABQSwECHgMKAAIAAAB5cT5cBUgYaQYAAAAGAAAAHAAYAAAAAAABAAAA/4GnAAAAbW9ja19hcmNoaXZlX2'
                           b'ZpbGVzL2ZpbGUxLnJvbVVUBQADVeZ8aXV4CwABBAAAAAAEAAAAAFBLAQIeAwoAAgAAAHtxPlwFSBhpBgAAAAYAAAAc'
                           b'ABgAAAAAAAEAAAD/gQMBAABtb2NrX2FyY2hpdmVfZmlsZXMvZmlsZTIuYmluVVQFAANZ5nxpdXgLAAEEAAAAAAQAAA'
                           b'AAUEsBAh4DCgAAAAAAVnE+XAAAAAAAAAAAAAAAABoAGAAAAAAAAAAQAP9BXwEAAG1vY2tfYXJjaGl2ZV9maWxlcy9m'
                           b'b2xkZXIvVVQFAAMT5nxpdXgLAAEEAAAAAAQAAAAAUEsBAh4DCgACAAAAhnE+XAVIGGkGAAAABgAAACMAGAAAAAAAAQ'
                           b'AAAP+BswEAAG1vY2tfYXJjaGl2ZV9maWxlcy9mb2xkZXIvZmlsZTMucG5nVVQFAANr5nxpdXgLAAEEAAAAAAQAAAAA'
                           b'UEsBAh4DCgACAAAAlnE+XAVIGGkGAAAABgAAAB0AGAAAAAAAAQAAAP+BFgIAAG1vY2tfYXJjaGl2ZV9maWxlcy9yZW'
                           b'FkbWUudHh0VVQFAAOL5nxpdXgLAAEEAAAAAAQAAAAAUEsFBgAAAAAHAAcArwIAAHMCAAAAAA==')

def test_listar_conteudo_zip(mocker_open, mocker):
    # setup arquivo zip no mock
    with open('arquivo.zip', "wb") as arquivo_zip:
        arquivo_zip.write(base64.b64decode(mock_zip_content_base64))
    fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
    fakechecamagic.return_value.detecta_tipo.return_value = ("TESTE", b"TESTE")
    from utils.descompactadores_utils import listar_conteudo_zip
    resultado = listar_conteudo_zip("arquivo.zip")
    close_all(mocker_open)
    # testa se o coletou os nomes dentro do zip corretamente
    assert set(resultado[0]) == set(mock_archive_files_list)
    # testa se os crc32 condizem ( 0 -> diretorio ou arquivo vazio)
    assert resultado[1] == [0, 0, 1763198981, 1763198981, 0, 1763198981, 1763198981]
    # testa se o objeto checamagic foi consultado corretamente
    assert resultado[2] == [('Diretorio', b''), ('Diretorio', b''), ('TESTE', b'TESTE'), ('TESTE', b'TESTE'),
                            ('Diretorio', b''), ('TESTE', b'TESTE'), ('TESTE', b'TESTE')]

def test_extrair_arquivo_zip_com_alvo_com_saida(mocker_open, mocker, monkeypatch):
    # setup arquivo zip no mock
    with open('arquivo.zip', "wb") as arquivo_zip:
        arquivo_zip.write(base64.b64decode(mock_zip_content_base64))
    nome_arquivo_zip = "arquivo.zip"
    destino_dir = "arquivo"
    nome_saida = "teste.out"
    alvo = "mock_archive_files/file1.rom"
    # tem que instalar o mocker antes de importar descompactadoes_utils por causa
    # do atributo detetor (ChecaMagic)
    fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
    # importar descompactadores_utils para poder instalar fake os mock
    import utils.descompactadores_utils
    # agora consigo instalar o mocker_open em fake_os e monkeypatch para rename
    fake_os = FakeOs(mocker_open)
    monkeypatch.setattr(utils.descompactadores_utils, "rename", fake_os.rename)
    monkeypatch.setattr("os.makedirs", fake_os.makedirs)
    utils.descompactadores_utils.extrair_arquivo_zip(nome_arquivo_zip, destino_dir, nome_saida, alvo)
    # coleta arquivos no mocker
    resultado = list(mocker_open.keys())
    close_all(mocker_open)
    # checa se todos os arquivos estao no lugar certo
    assert {"arquivo.zip", "arquivo\\teste.out"}.issubset(set(resultado))

def test_extrair_arquivo_zip_sem_alvo_sem_saida(mocker_open, mocker, monkeypatch):
    # setup arquivo zip no mock
    with open('arquivo.zip', "wb") as arquivo_zip:
        arquivo_zip.write(base64.b64decode(mock_zip_content_base64))
    nome_arquivo_zip = "arquivo.zip"
    destino_dir = "arquivo"
    nome_saida = ""
    alvo = ""
    fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
    import utils.descompactadores_utils
    fakeos = FakeOs(mocker_open)
    monkeypatch.setattr("os.makedirs", fakeos.makedirs)
    monkeypatch.setattr(utils.descompactadores_utils, "makedirs", fakeos.makedirs)
    utils.descompactadores_utils.extrair_arquivo_zip(nome_arquivo_zip, destino_dir, nome_saida, alvo)
    lista_arquivos_extraidos = extracted_archive_file_list[:]
    lista_arquivos_extraidos.append("arquivo.zip")
    resultado = set(mocker_open.keys())
    close_all(mocker_open)
    # testa se todos os arquivos esperados foram extraidos
    assert resultado == set(lista_arquivos_extraidos)

#  tests suporte 7zip
mock_7zip_content_base64 = (b'N3q8ryccAAQJj3HT4AAAAAAAAAAiAAAAAAAAAKcaroXgABcADF0AKhFGuBDrOUurSAAAAAAAgTMHrg/PObAMB8hDf'
                            b'0Gx+v3uh/gFMt8DtGuT9Wkhwfc4o2h1xBhZPaopW1MVwRUJ8T+532/wFXFG/ORbbGcTuXoL6KSoDJ9SHC/yqZbzqK'
                            b'tk0qVB1oFelZdAActNUHepaFbWtbTV0a+lOBpaax8wda5vgHVDve+HaotqAv1ZsJuA4EUUNIZEG7n9b6fbFI8BISt'
                            b'P03iOqZcVedwo+g2rsq3BxGHXnmYgN7i+1u+/ecJW+tHXWcxvITjK5ExlDQG/hll0ExgctgAAABcGFAEJgMwABwsB'
                            b'AAEjAwEBBV0AEAAADIIyCgHpqXimAAA=')

def test_listar_conteudo_7zip(mocker_open, mocker):
    # setup arquivo 7zip no mock
    with open('arquivo.7z', "wb") as arquivo_comprimido:
        arquivo_comprimido.write(base64.b64decode(mock_7zip_content_base64))
    fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
    fakechecamagic.return_value.detecta_tipo.return_value = ("TESTE", b"TESTE")
    from utils.descompactadores_utils import listar_conteudo_com_7z
    resultado = listar_conteudo_com_7z("arquivo.7z")
    close_all(mocker_open)
    # testa se o coletou os nomes dentro do 7zip corretamente
    assert set(resultado[0]) == set(mock_archive_files_list)
    # testa se os crc32 condizem ( 0 -> diretorio ou arquivo vazio)
    assert resultado[1] == [0, 0, 1763198981, 1763198981, 0, 1763198981, 1763198981]
    # testa se o objeto checamagic foi consultado corretamente
    assert resultado[2] == [('Diretorio', b''), ('Diretorio', b''), ('TESTE', b'TESTE'), ('TESTE', b'TESTE'),
                            ('Diretorio', b''), ('TESTE', b'TESTE'), ('TESTE', b'TESTE')]

def test_extrair_arquivo_7zip_com_alvo_com_saida(mocker_open, monkeypatch):
    # setup arquivo zip no mock
    with open('arquivo.7z', "wb") as arquivo_7z:
        arquivo_7z.write(base64.b64decode(mock_7zip_content_base64))
    nome_arquivo = "arquivo.7z"
    destino_dir = "c:\\arquivo"
    nome_saida = "teste.out"
    alvo = "mock_archive_files/file1.rom"
    # tem que instalar o mocker antes de importar descompiladores_utils por causa
    # do atributo detetor (ChecaMagic)
    # fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
    # importar descompactadores_utils para poder instalar fake os mock
    import utils.descompactadores_utils
    # agora consigo instalar o mocker_open em fake_os e monkeypatch para rename
    fake_os = FakeOs(mocker_open)
    monkeypatch.setattr(utils.descompactadores_utils, "rename", fake_os.rename)
    # mocks para os.utime e os.makedirs
    monkeypatch.setattr("os.utime", fake_os.utime)
    monkeypatch.setattr(utils.descompactadores_utils, "makedirs", fake_os.makedirs)
    # 7zip utiliza biblioteca pathlib.Path para escritas, a maior diferenca eh que sao
    # metodos de instancia e precisam ser patcheadas na classe.
    interceptador_mkdir = criar_interceptador_self_kwargs(lambda x, **_: fake_os.makedirs(str(x)))
    monkeypatch.setattr("pathlib.Path.mkdir", interceptador_mkdir)
    interceptador_open = criar_interceptador_self_kwargs(lambda x, **kwargs: open(str(x), kwargs["mode"]))
    monkeypatch.setattr('pathlib.Path.open', interceptador_open)
    #finalmente chamamos o metodo em teste
    utils.descompactadores_utils.extrair_arquivo_com_7zip(nome_arquivo, destino_dir, nome_saida, alvo)
    # coleta arquivos no mocker
    resultado = list(mocker_open.keys())
    close_all(mocker_open)
    # checa se todos os arquivos estao no lugar certo
    assert {"arquivo.7z", "c:\\arquivo\\teste.out"}.issubset(set(resultado))

def test_extrair_arquivo_7zip_sem_alvo_sem_saida(mocker_open, monkeypatch):
    # setup arquivo zip no mock
    with open('arquivo.7z', "wb") as arquivo_7z:
        arquivo_7z.write(base64.b64decode(mock_7zip_content_base64))
    nome_arquivo = "arquivo.7z"
    destino_dir = "c:\\arquivo"
    nome_saida = ""
    alvo = ""
    # tem que instalar o mocker antes de importar descompiladores_utils por causa
    # do atributo detetor (ChecaMagic)
    # fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
    # importar descompactadores_utils para poder instalar fake os mock
    import utils.descompactadores_utils
    # agora consigo instalar o mocker_open em fake_os e monkeypatch para rename
    fake_os = FakeOs(mocker_open)
    monkeypatch.setattr(utils.descompactadores_utils, "rename", fake_os.rename)
    monkeypatch.setattr("os.utime", fake_os.utime)
    monkeypatch.setattr(utils.descompactadores_utils, "makedirs", fake_os.makedirs)
    interceptador_mkdir = criar_interceptador_self_kwargs(lambda x, **_: fake_os.makedirs(str(x)))
    monkeypatch.setattr("pathlib.Path.mkdir", interceptador_mkdir)
    interceptador_open = criar_interceptador_self_kwargs(lambda x, **kwargs: open(str(x), kwargs["mode"]))
    monkeypatch.setattr('pathlib.Path.open', interceptador_open)
    utils.descompactadores_utils.extrair_arquivo_com_7zip(nome_arquivo, destino_dir, nome_saida, alvo)
    # coleta arquivos no mocker
    resultado = set(mocker_open.keys())
    # altera a lista dos arquivo esperados para refletir as condicoes do teste
    lista_arquivos_extraidos = extracted_archive_file_list[:]
    lista_arquivos_extraidos = list(map(lambda x: "c:\\" + x, lista_arquivos_extraidos))
    lista_arquivos_extraidos.append("arquivo.7z")
    close_all(mocker_open)
    # checa se todos os arquivos estao no lugar certo
    assert set(lista_arquivos_extraidos).issubset(resultado)

# teste suporte a .lha
mock_lha_content_base64 = (b'SQAtbGhkLQAAAAAAAAAAveV8aSACAABVBQAA+SgDAAEWAAJtb2NrX2FyY2hpdmVfZmlsZXP/BQBQtkEHAFEAAAAABQ'
                           b'BTcGMAAFYALWxoZC0AAAAAAAAAAFXCe2kgAgAAVQUAAAYJAwABIwACbW9ja19hcmNoaXZlX2ZpbGVz/2VtcHR5X2Zv'
                           b'bGRlcv8FAFC2QQcAUQAAAAAFAFNwYwAAUgAtbGgwLQYAAAAGAAAAVeZ8aSACIhhVBQAAl5wMAAFmaWxlMS5yb20WAA'
                           b'Jtb2NrX2FyY2hpdmVfZmlsZXP/BQBQtoEHAFEAAAAABQBTcGMAAFRFU1RFClIALWxoMC0GAAAABgAAAFnmfGkgAiIY'
                           b'VQUAAEFmDAABZmlsZTIuYmluFgACbW9ja19hcmNoaXZlX2ZpbGVz/wUAULaBBwBRAAAAAAUAU3BjAABURVNURQpQAC'
                           b'1saGQtAAAAAAAAAAAT5nxpIAIAAFUFAAA2MwMAAR0AAm1vY2tfYXJjaGl2ZV9maWxlc/9mb2xkZXL/BQBQtkEHAFEA'
                           b'AAAABQBTcGMAAFkALWxoMC0GAAAABgAAAGvmfGkgAiIYVQUAAEhpDAABZmlsZTMucG5nHQACbW9ja19hcmNoaXZlX2'
                           b'ZpbGVz/2ZvbGRlcv8FAFC2gQcAUQAAAAAFAFNwYwAAVEVTVEUKUwAtbGgwLQYAAAAGAAAAi+Z8aSACIhhVBQAAYJkN'
                           b'AAFyZWFkbWUudHh0FgACbW9ja19hcmNoaXZlX2ZpbGVz/wUAULaBBwBRAAAAAAUAU3BjAABURVNURQoA')

def test_listar_conteudo_lha(mocker):
    # setup arquivo lha no mock
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_arquivo_lha = tmpdir + '\\' + 'arquivo.lha'
        with open(caminho_arquivo_lha, "wb") as arquivo_comprimido:
            arquivo_comprimido.write(base64.b64decode(mock_lha_content_base64))
        fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
        fakechecamagic.return_value.detecta_tipo.return_value = ("TESTE", b"TESTE")
        from utils.descompactadores_utils import listar_conteudo_pma
        resultado = listar_conteudo_pma(caminho_arquivo_lha)
        # testa se o coletou os nomes dentro do lha corretamente
        assert set(resultado[0]) == set(mock_archive_files_list)
        # testa se os crc32 condizem ( 0 -> diretorio ou arquivo vazio)
        assert resultado[1] == [0, 0, 1763198981, 1763198981, 0, 1763198981, 1763198981]
        # testa se o objeto checamagic foi consultado corretamente
        assert resultado[2] == [('Diretorio', b''), ('Diretorio', b''), ('TESTE', b'TESTE'), ('TESTE', b'TESTE'),
                                ('Diretorio', b''), ('TESTE', b'TESTE'), ('TESTE', b'TESTE')]

def test_extrair_arquivo_lha_com_alvo_com_saida(mocker, monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_arquivo_lha = tmpdir + '\\' + 'arquivo.lha'
        # setup arquivo lha no mock
        with open(caminho_arquivo_lha, "wb") as arquivo_lha:
            arquivo_lha.write(base64.b64decode(mock_lha_content_base64))
        nome_saida = "teste.out"
        destino = tmpdir + "\\arquivo"
        alvo = "mock_archive_files/file1.rom"
        # tem que instalar o mocker antes de importar descompactadoes_utils por causa
        # do atributo detetor (ChecaMagic)
        fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
        # importar descompactadores_utils para poder instalar fake os mock
        import utils.descompactadores_utils
        utils.descompactadores_utils.extrair_arquivo_pma(caminho_arquivo_lha, destino, nome_saida, alvo)
        # coleta arquivos no mocker
        from utils.arquivo_util import lista_todos_arquivos_no_caminho
        resultado = lista_todos_arquivos_no_caminho(tmpdir,relativo=True)
        # checa se todos os arquivos estao no lugar certo
        assert {"arquivo.lha", "arquivo\\teste.out"}.issubset(set(resultado))

def test_extrair_arquivo_lha_sem_alvo_sem_saida(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_arquivo_lha = tmpdir + '\\' + 'arquivo.lha'
        # setup arquivo lha no mock
        # setup arquivo lha no mock
        with open(caminho_arquivo_lha, "wb") as arquivo_lha:
            arquivo_lha.write(base64.b64decode(mock_lha_content_base64))
        destino = tmpdir + "\\arquivo"
        nome_saida = ""
        alvo = ""
        # tem que instalar o mocker antes de importar descompiladores_utils por causa
        # do atributo detetor (ChecaMagic)
        # fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
        # importar descompactadores_utils para poder instalar fake os mock
        import utils.descompactadores_utils
        utils.descompactadores_utils.extrair_arquivo_pma(caminho_arquivo_lha, destino, nome_saida, alvo)
        # altera a lista dos arquivo esperados para refletir as condicoes do teste
        lista_arquivos_extraidos_esperada = extracted_archive_file_list[:]
        lista_arquivos_extraidos_esperada.append("arquivo.lha")
        # checa se todos os arquivos estao no lugar certo
        from utils.arquivo_util import lista_todos_arquivos_no_caminho
        resultado = lista_todos_arquivos_no_caminho(tmpdir,relativo=True, inclui_subdirs=True)
        assert set(lista_arquivos_extraidos_esperada).issubset(resultado)

mock_arj_content_base64 = (b'YOowACILAQsQAAIDA2RFXANkRVwAAAAAAAAAAAAAAAAAAAAAAABtb2NrX2Fyai5hcmoAAFTFv5gAAGDqUwAuCwELEA'
                           b'AAA4ZxPlwGAAAABgAAAAVIGGkaACAAAAAAAAAAhnE+XEZxPlwAAAAAbW9ja19hcmNoaXZlX2ZpbGVzL2ZvbGRlci9m'
                           b'aWxlMy5wbmcAADNGwvUAAFRFU1RFCmDqTwAuCwMLEAADAz2LPVwAAAAAAAAAAAAAAAATABAAAAAAAAAAPYs9XD2LPV'
                           b'wAAAAAbW9ja19hcmNoaXZlX2ZpbGVzL2VtcHR5X2ZvbGRlcgAAy6B64QAAYOpMAC4LAQsQAAADeXE+XAYAAAAGAAAA'
                           b'BUgYaRMAIAAAAAAAAAB5cT5cGIs9XAAAAABtb2NrX2FyY2hpdmVfZmlsZXMvZmlsZTEucm9tAABoD8NfAABURVNURQ'
                           b'pg6kwALgsBCxAAAAN7cT5cBgAAAAYAAAAFSBhpEwAgAAAAAAAAAHtxPlwciz1cAAAAAG1vY2tfYXJjaGl2ZV9maWxl'
                           b'cy9maWxlMi5iaW4AAGChLyEAAFRFU1RFCmDqSQAuCwMLEAADA1ZxPlwAAAAAAAAAAAAAAAATABAAAAAAAAAAVnE+XC'
                           b'eLPVwAAAAAbW9ja19hcmNoaXZlX2ZpbGVzL2ZvbGRlcgAAaBJMPQAAYOpNAC4LAQsQAAADlnE+XAYAAAAGAAAABUgY'
                           b'aRMAIAAAAAAAAACWcT5cI4s9XAAAAABtb2NrX2FyY2hpdmVfZmlsZXMvcmVhZG1lLnR4dAAAZJvCUQAAVEVTVEUKYO'
                           b'oAAA==')

def test_listar_conteudo_arj(mocker):
    # setup arquivo arj no mock
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_arquivo_arj = tmpdir + '\\' + 'arquivo.arj'
        with open(caminho_arquivo_arj, "wb") as arquivo_comprimido:
            arquivo_comprimido.write(base64.b64decode(mock_arj_content_base64))
        fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
        fakechecamagic.return_value.detecta_tipo.return_value = ("TESTE", b"TESTE")
        from utils.descompactadores_utils import listar_conteudo_arj
        resultado = listar_conteudo_arj(caminho_arquivo_arj)
        # testa se o coletou os nomes dentro do arj corretamente
        assert set(resultado[0]) == set(mock_archive_files_list)
        # testa se os crc32 condizem ( 0 -> diretorio ou arquivo vazio)
        resultado[1].sort()
        assert resultado[1] == [0, 0, 0, 1763198981, 1763198981, 1763198981, 1763198981]
        # testa se o objeto checamagic foi consultado corretamente
        resultado[2].sort()
        assert resultado[2] == [('Diretorio', b''), ('Diretorio', b''), ('Diretorio', b''), ('TESTE', b'TESTE'),
                                ('TESTE', b'TESTE'), ('TESTE', b'TESTE'), ('TESTE', b'TESTE')]

def test_extrair_arquivo_arj_com_alvo_com_saida(mocker, monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_arquivo_arj = tmpdir + '\\' + 'arquivo.arj'
        # setup arquivo arj no mock
        with open(caminho_arquivo_arj, "wb") as arquivo_arj:
            arquivo_arj.write(base64.b64decode(mock_arj_content_base64))
        nome_saida = "teste.out"
        destino = tmpdir + "\\arquivo"
        alvo = "mock_archive_files/file1.rom"
        # tem que instalar o mocker antes de importar descompactadoes_utils por causa
        # do atributo detetor (ChecaMagic)
        fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
        # importar descompactadores_utils para poder instalar fake os mock
        import utils.descompactadores_utils
        utils.descompactadores_utils.extrair_arquivo_arj(caminho_arquivo_arj, destino, nome_saida, alvo)
        # coleta arquivos no mocker
        from utils.arquivo_util import lista_todos_arquivos_no_caminho
        resultado = lista_todos_arquivos_no_caminho(tmpdir,relativo=True)
        # checa se todos os arquivos estao no lugar certo
        assert {"arquivo.arj", "arquivo\\teste.out"}.issubset(set(resultado))

def test_extrair_arquivo_arj_sem_alvo_sem_saida(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_arquivo_arj = tmpdir + '\\' + 'arquivo.arj'
        # setup arquivo arj no mock
        with open(caminho_arquivo_arj, "wb") as arquivo_arj:
            arquivo_arj.write(base64.b64decode(mock_arj_content_base64))
        destino = tmpdir + "\\arquivo"
        nome_saida = ""
        alvo = ""
        # tem que instalar o mocker antes de importar descompiladores_utils por causa
        # do atributo detetor (ChecaMagic)
        # fakechecamagic = mocker.patch("checa_magic.classe_checa_magic.ChecaMagic")
        # importar descompactadores_utils para poder instalar fake os mock
        import utils.descompactadores_utils
        utils.descompactadores_utils.extrair_arquivo_arj(caminho_arquivo_arj, destino, nome_saida, alvo)
        # altera a lista dos arquivo esperados para refletir as condicoes do teste
        lista_arquivos_extraidos_esperada = extracted_archive_file_list[:]
        lista_arquivos_extraidos_esperada.append("arquivo.arj")
        # checa se todos os arquivos estao no lugar certo
        from utils.arquivo_util import lista_todos_arquivos_no_caminho
        resultado = lista_todos_arquivos_no_caminho(tmpdir,relativo=True, inclui_subdirs=True)
        assert set(lista_arquivos_extraidos_esperada).issubset(resultado)
