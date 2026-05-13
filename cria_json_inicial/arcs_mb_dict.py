from criador_json import criador_json as cj
import valores_globais

# carrega valores das opcoes em "conf/arcs_mb.json" ou cria arquivo a partir deste json padrão.
json_inicial = (
    '{\n'
    '  "json_ver": 1,\n'
    '  "000000504B0304": "ZIP",\n'
    '  "000000377ABCAF271C": "7Z",\n'
    '  "000000FD377A585A00": "XZ",\n'
    '  "0000001F8B08": "GZ",\n'
    '  "000000425a68": "BZ2",\n'
    '  "0000022D6C68302D": "LHA LZH",\n'
    '  "0000022D6C68312D": "LHA LZH",\n'
    '  "0000022D6C7A342D": "LHA LZH",\n'
    '  "0000022D6C7A352D": "LHA LZH",\n'
    '  "0000022D6C7A732D": "LHA LZH",\n'
    '  "0000022D6C68402D": "LHA LZH",\n'
    '  "0000022D6C68642D": "LHA LZH",\n'
    '  "0000022D6C68322D": "LHA LZH",\n'
    '  "0000022D6C68332D": "LHA LZH",\n'
    '  "0000022D6C68342D": "LHA LZH",\n'
    '  "0000022D6C68352D": "LHA LZH",\n'
    '  "0000022D706D302D": "PMA",\n'
    '  "0000022D706D312D": "PMA",\n'
    '  "0000022D706D322D": "PMA",\n'
    '  "000101757374617200": "TAR",\n'
    '  "00000060EA": "ARJ",\n'
    '  "000000526172211A07": "RAR"\n'
    '}'
)
cj.verbose = valores_globais.debug
arcs_mb_dict = cj.carrega_ou_cria_config("conf/arcs_mb.json", json_inicial)
