from criador_json import criador_json as cj

# carrega "dados_tipo.json" com dados dos tipos (cmd, ext e dos) ou cria arquivo a partir deste json padrão
dados_tipo_json_inicial = (
    '{\n'
    '  "json_ver": 0,\n'
    '  "DOSBOX": {\n'
    '    "cmd": ["C:\\\\Program Files (x86)\\\\DOSBox-0.74-3\\\\DOSBox.exe", "-fullscreen", "-c", "mount e: e:/",\n'
    '      "-c", "e:", "-c", "cd ?d", "-c", "00dosbox.bat"],\n'
    '    "ext": ["00dosbox.bat"],\n'
    '    "dos": true,\n'
    '    "extrai_tudo": true\n'
    '  },\n'
    '  "MSXDSK BRMSX": {\n'
    '    "cmd": ["C:\\\\Program Files (x86)\\\\DOSBox-0.74-3\\\\DOSBox.exe", "-fullscreen", "-c", "mount e: e:/",\n'
    '      "-c", "mount c: D:\\\\emul\\\\msx\\\\brmsx\\\\dos", "-c", "c:", "-c",\n'
    '      "BRMSX -noenter -mapper 4 -diska ?c", "-c", "exit"],\n'
    '    "ext": ["dsk"],\n'
    '    "dos": true,\n'
    '    "extrai_tudo": false\n'
    '  }\n'
    '}'
)
dados_tipo = cj.carrega_ou_cria_config("dados_tipo.json", dados_tipo_json_inicial)
