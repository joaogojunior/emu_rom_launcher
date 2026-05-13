from tests.helper_mock_os import FakeOs, mocker_open, close_all


def test_lista_todos_arquivos_no_caminho_absoluto(monkeypatch, mocker_open):
    import utils.arquivo_util
    valor_retorno = ["c:\\tmp\\fake_dir\\file1.txt", "c:\\tmp\\fake_dir\\subdir\\file2.txt"]
    for arquivo in valor_retorno:
        with open(arquivo, "w") as arquivo_handler:
            arquivo_handler.write("")
    fakeos = FakeOs(mocker_open)
    # Patch os.walk and set its return value to the mock generator
    monkeypatch.setattr(utils.arquivo_util, "walk", fakeos.walk)
    close_all(mocker_open)
    resultado = utils.arquivo_util.lista_todos_arquivos_no_caminho(
        "c:\\tmp\\fake_dir", relativo=False, inclui_subdirs=False)
    assert resultado == valor_retorno


def test_lista_todos_arquivos_no_caminho_relativo(monkeypatch, mocker_open):
    import utils.arquivo_util
    arquivos = ["c:\\tmp\\fake_dir\\file1.txt", "c:\\tmp\\fake_dir\\subdir\\file2.txt"]
    for arquivo in arquivos:
        with open(arquivo, "w") as arquivo_handler:
            arquivo_handler.write("")
    fakeos = FakeOs(mocker_open)
    # Patch os.walk and set its return value to the mock generator
    monkeypatch.setattr(utils.arquivo_util, "walk", fakeos.walk)
    valor_retorno = ["file1.txt", "subdir\\file2.txt"]
    resultado = utils.arquivo_util.lista_todos_arquivos_no_caminho(
        "c:\\tmp\\fake_dir", relativo=True, inclui_subdirs=False)
    close_all(mocker_open)
    assert resultado == valor_retorno


def test_lista_todos_arquivos_no_caminho_relativo_inclui_diretorios_vazios_relativos(monkeypatch, mocker_open):
    import utils.arquivo_util
    arquivos = ["c:\\tmp\\fake_dir\\file1.txt", "c:\\tmp\\fake_dir\\subdir\\file2.txt"]
    for arquivo in arquivos:
        with open(arquivo, "w") as arquivo_handler:
            arquivo_handler.write("")
    fakeos = FakeOs(mocker_open)
    fakeos.makedirs("c:\\tmp\\fake_dir\\empty_dir")
    # Patch os.walk and set its return value to the mock generator
    monkeypatch.setattr(utils.arquivo_util, "walk", fakeos.walk)
    valor_retorno = ["file1.txt", "subdir\\file2.txt", "subdir\\", "empty_dir\\"]
    resultado = utils.arquivo_util.lista_todos_arquivos_no_caminho(
        "c:\\tmp\\fake_dir", relativo=True, inclui_subdirs=True)
    close_all(mocker_open)
    assert set(resultado) == set(valor_retorno)


def test_lista_todos_arquivos_no_caminho_relativo_inclui_diretorios_vazios_absolutos(monkeypatch, mocker_open):
    import utils.arquivo_util
    arquivos = ["c:\\tmp\\fake_dir\\file1.txt", "c:\\tmp\\fake_dir\\subdir\\file2.txt"]
    for arquivo in arquivos:
        with open(arquivo, "w") as arquivo_handler:
            arquivo_handler.write("")
    fakeos = FakeOs(mocker_open)
    fakeos.makedirs("c:\\tmp\\fake_dir\\empty_dir")
    # Patch os.walk and set its return value to the mock generator
    monkeypatch.setattr(utils.arquivo_util, "walk", fakeos.walk)
    valor_retorno = ["c:\\tmp\\fake_dir\\file1.txt", "c:\\tmp\\fake_dir\\subdir\\file2.txt",
                     "c:\\tmp\\fake_dir\\empty_dir\\", "c:\\tmp\\fake_dir\\subdir\\"]
    resultado = utils.arquivo_util.lista_todos_arquivos_no_caminho(
        "c:\\tmp\\fake_dir", relativo=False, inclui_subdirs=True)
    close_all(mocker_open)
    assert set(resultado) == set(valor_retorno)


def test_copia_arquivo(mocker_open):
    import utils.arquivo_util
    # cria arquivo no mocker_open
    with open("origem.txt", "wb") as arquivo_teste:
        arquivo_teste.write(b"isso eh um teste.\n")
    utils.arquivo_util.copia_arquivo("origem.txt", "teste/destino.txt")
    buffer = mocker_open["teste/destino.txt"]
    buffer.seek(0)
    conteudo = buffer.read()
    close_all(mocker_open)
    assert conteudo == b"isso eh um teste.\n"
