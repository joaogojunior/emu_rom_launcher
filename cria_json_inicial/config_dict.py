from criador_json import criador_json as cj
import valores_globais

# carrega valores das opcoes em "conf/config.json" ou cria arquivo a partir deste json padrão.
json_inicial = (
    '{\n'
    '  "json_ver": 2,\n'
    '  "caminho_temp_dir": "r:\\\\",\n'
    '  "arquivo_rom": "",\n'
    '  "converte_espacos_em_underscore": 1,\n'
    '  "caminho_7zip": "C:\\\\Program Files\\\\7-Zip\\\\7z.exe",\n'
    '  "alvos_prioritarios": ["00dosbox.bat", "msxdos.sys", "msxdos2.sys"],\n'
    '  "tam_ramdrive": "740M",\n'
    '  "format_ramdrive": "/FS:FAT32 /Q /y",\n'
    '  "encoding_padrao": "cp850",\n'
    '  "tempo_espera_caminho": 30,\n'
    '  "tempo_espera_escolha": 20,\n'
    '  "enter_para_fechar": 1,\n'
    '  "carregar_save_auto": 1,\n'
    '  "salvar_mesmo_arquivo": 1,\n'
    '  "escolhe_primeiro_se_iguais": 0,\n'
    '  "conferir_extensao_para_tipo_detectado": 0\n'
    '}'
)
cj.verbose = valores_globais.debug
config_dict = cj.carrega_ou_cria_config("conf/config.json", json_inicial)
