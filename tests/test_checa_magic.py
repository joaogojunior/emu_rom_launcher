import io

from tests.helper_mock_os import mocker_open, close_all

def test_checa_magic_carrega_json_corretamente(mocker_open):
    import checa_magic.classe_checa_magic as checa_magic
    # create a test json config
    with open("test.json", "wb") as testfile:
        testfile.write(b'{"json_ver": 1, "000000010203": "TEST"}')
    detector = checa_magic.ChecaMagic("test.json")
    close_all(mocker_open)
    assert detector.mb_tipos_dict == {"000000010203": "TEST"}

def test_detecta_tipo_arquivo(mocker_open):
    import checa_magic.classe_checa_magic as checa_magic
    # create a test json config
    with open("test.json", "wb") as configfile:
        configfile.write(b'{"json_ver": 1, "0000005445535445": "TESTE"}')
    #create arquivo de teste com a assinatura
    with open("arquivo_test.txt", "wb") as testfile:
        testfile.write(b"TESTE\n")
    detector = checa_magic.ChecaMagic("test.json")
    tipo_detectado = detector.detecta_tipo("arquivo_test.txt")
    close_all(mocker_open)
    assert tipo_detectado == ("TESTE", "0000005445535445")

def test_detecta_tipo_buffer(mocker_open):
    import checa_magic.classe_checa_magic as checa_magic
    # create a test json config
    with open("test.json", "wb") as configfile:
        configfile.write(b'{"json_ver": 1, "0000005445535445": "TESTE"}')
    buffer = io.BytesIO(b"TESTE\n")
    detector = checa_magic.ChecaMagic("test.json")
    tipo_detectado = detector.detecta_tipo(buffer)
    close_all(mocker_open)
    assert tipo_detectado == ("TESTE", "0000005445535445")

def test_funcao_obtem_ponteir_e_cmp_com_fita(mocker_open):
    import checa_magic.classe_checa_magic as checa_magic
    # create a test json config
    with open("test.json", "wb") as configfile:
        configfile.write(b'{"json_ver": 1, "000000544553.2=54=45": "TESTE"}')
    buffer = io.BytesIO(b"TES\x05\x00TE")
    detector = checa_magic.ChecaMagic("test.json")
    tipo_detectado = detector.detecta_tipo(buffer)
    close_all(mocker_open)
    assert tipo_detectado == ("TESTE", "000000544553.2=54=45")

def test_funcao_avanca_bytes_obtem_ponteir_e_cmp_com_fita(mocker_open):
    import checa_magic.classe_checa_magic as checa_magic
    # create a test json config
    with open("test.json", "wb") as configfile:
        configfile.write(b'{"json_ver": 1, "000000544553>6>.2=54=45": "TESTE"}')
    buffer = io.BytesIO(b"TES    \x09\x00TE")
    detector = checa_magic.ChecaMagic("test.json")
    tipo_detectado = detector.detecta_tipo(buffer)
    close_all(mocker_open)
    assert tipo_detectado == ("TESTE", "000000544553>6>.2=54=45")

def test_funcao_le_mais_bytes_e_cmp_com_fita_igualdade(mocker_open):
    import checa_magic.classe_checa_magic as checa_magic
    # create a test json config
    with open("test.json", "wb") as configfile:
        configfile.write(b'{"json_ver": 1, "000000544553+2-=54=45": "TESTE"}')
    buffer = io.BytesIO(b"TESTE")
    detector = checa_magic.ChecaMagic("test.json")
    tipo_detectado = detector.detecta_tipo(buffer)
    close_all(mocker_open)
    assert tipo_detectado == ("TESTE", "000000544553+2-=54=45")

def test_funcao_le_mais_bytes_e_cmp_com_fita_intervalo(mocker_open):
    import checa_magic.classe_checa_magic as checa_magic
    # create a test json config
    with open("test.json", "wb") as configfile:
        configfile.write(b'{"json_ver": 1, "000000544553+2-53544546": "TESTE"}')
    buffer = io.BytesIO(b"TESTE")
    buffer2 = io.BytesIO(b"TESSF")
    buffer3 = io.BytesIO(b"TESSG")
    detector = checa_magic.ChecaMagic("test.json")
    tipo_detectado = detector.detecta_tipo(buffer)
    tipo_detectado2 = detector.detecta_tipo(buffer2)
    tipo_detectado3 = detector.detecta_tipo(buffer3)
    close_all(mocker_open)
    assert tipo_detectado == ("TESTE", "000000544553+2-53544546")
    assert tipo_detectado2 == ("TESTE", "000000544553+2-53544546")
    assert tipo_detectado3[0] == "Desconhecido"

def test_funcao_avanca_bytes_le_mais_bytes_e_cmp_com_fita(mocker_open):
    import checa_magic.classe_checa_magic as checa_magic
    # create a test json config
    with open("test.json", "wb") as configfile:
        configfile.write(b'{"json_ver": 1, "0000004D5A>22>+2-=00=00": "TESTE"}')
    buffer = io.BytesIO(b"MZ                      \x00\x00")
    detector = checa_magic.ChecaMagic("test.json")
    tipo_detectado = detector.detecta_tipo(buffer)
    close_all(mocker_open)
    assert tipo_detectado == ("TESTE", "0000004D5A>22>+2-=00=00")
