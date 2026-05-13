def cria_arquivos():
    debug = True

    # nome de arquivo python, local do arquivo json, variavel dentro do scripy python
    lista_arquivos_para_criar = (
        ("config_dict.py", "conf/config.json", "config_dict"),
        ("dados_tipo_dict.py", "conf/dados_tipo.json", "dados_tipo"),
        ("descompactadores_dict.py", "conf/descompactadores.json", "descompactadores"),
        ("arcs_mb_dict.py", "conf/arcs_mb.json", "arcs_mb_dict"),
        ("roms_mb_dict.py", "conf/roms_mb.json", "roms_mb_dict")
    )

    for nome_arquivo_py, caminho_arquivo_json, variavel_py in lista_arquivos_para_criar:
        prefixo_arquivos_py = "from criador_json import criador_json as cj\nimport valores_globais\n\n# carrega valores das opcoes em \"" + caminho_arquivo_json + "\" ou cria arquivo a partir deste json padrão.\njson_inicial = (\n"
        sufixo_arquivos_py = "\n)\ncj.verbose = valores_globais.debug\n" + variavel_py + " = cj.carrega_ou_cria_config(\"" + caminho_arquivo_json + "\", json_inicial)\n"
        with open(caminho_arquivo_json, 'r', encoding='utf-8') as f:
            # Processa cada linha individualmente com repr() e junta com quebras de linha reais
            linhas_formatadas_json = '\n'.join("    " + repr(linha) for linha in f.readlines())
            # Para criar a representação de variável pronta para copiar
            conteudo = prefixo_arquivos_py + linhas_formatadas_json + sufixo_arquivos_py
            if debug:
                print("___________________________")
                print(conteudo)
            # cria arquivo
            with open("cria_json_inicial/" + nome_arquivo_py, 'w', encoding='utf-8') as arquivo_saida:
                arquivo_saida.write(conteudo)
