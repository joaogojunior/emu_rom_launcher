from criador_json import criador_json as cj

# carrega valores das opcoes em "config.json" ou cria arquivo a partir deste json padrão
config_json_inicial = (
    '{\n'
    '  "json_ver": 0,\n'
    '  "caminho_temp_dir": "e:\\\\",\n'
    '  "arquivo_rom": "",\n'
    '  "abre_arquivador": "C:\\\\Program Files\\\\7-Zip\\\\7zFM.exe",\n'
    '  "alvos_prioritarios": ["00dosbox.bat", "msxdos.sys"],\n'
    '  "tam_ramdrive": "64M",\n'
    '  "format_ramdrive": "/FS:FAT32 /Q /y",\n'
    '  "tempo_espera_caminho": 30,\n'
    '  "tempo_espera_escolha": 10\n'
    '}'
)
config_dict = cj.carrega_ou_cria_config("conf/config.json", config_json_inicial)
