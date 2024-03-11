# import da data atual
from pyinstaller_build_date import data_hora_build
from descompactadores_dict import descompactadores

# versao atual
VER = "0.1g"

# descricao do app utilizado pelo argparser e na criacao do readme.txt
description_text = "Emu_rom_launcher v" + VER + " - tenta detectar o tipo de rom e executa o emulador apropiado."

# texto do credito mostrado durante a inicializacao e na criacao do readme.txt
creditos_text = ("emu_rom_launcher v" + VER + " programado por joaogojunior@gmail.com e lançado em " +
                 data_hora_build)

lista_suportada = list(descompactadores.keys())
ultimo_item = lista_suportada[-1]
lista_suportada = " ".join(lista_suportada[:-1]) + " e " + ultimo_item
# texto do help descrevendo caminho_arquivo utilizado pelo argparser e na criacao do readme.txt
caminho_text = (f'Caminho para o arquivo rom sendo este o argumento necessário para a operação\n'
                'normal. Arquivos compactados nos seguintes formatos são suportados: ' +
                lista_suportada[:8] + "\n" + lista_suportada[9:] + ".")

# texto do help descrevendo opcao -r utilizado pelo argparser e na criação de readme.txt
remove_text = "Remove a unidade ramdrive ativa e configurada em \"caminho_temp_dir\"."

# texto formatado manualmente utilizado pelo argparser e na criação do readme.txt
epilog_text = (
    f'Os caminhos e parâmetros dos emuladores devem ser configurados no arquivo dados_tipo.json.\n'
    '\n'
    'Na plataforma windows todos os caminhos especificados nos arquivos de configuração e de tipos\n'
    'devem conter "\\\\" (duplas barras) ao invés de "\\" (apenas uma barra). Isso é devido ao caractere\n'
    '"\\" ter significados especiais no contexto dos ambientes utilizados e utilizando duplas barras torna\n'
    'claro para o sistema que elas devem ser tratadas internamente como uma só barra quando for acessar os\n'
    'arquivos evitando erros e ambiguidades.\n'
    '\n'
    'Descrição das opções no arquivo config.json:\n'
    '\n'
    '"caminho_temp_dir": "e:\\\\" - Utiliza unidade e: como unidade ramdrive temporária (imdisk deve ser\n'
    'instalado previamente), certifique-se de escolher uma letra de unidade disponível caso já exista\n'
    'uma unidade e:\\ no seu computador.\n'
    '\n'
    '"alvos_prioritarios": ["00dosbox.bat", "msxdos.sys"] - lista de alvos com prioridade de escolha sobre\n'
    'os outros. Alvos mais a esquerda tem mais prioridade que um alvo mais a direita.\n'
    '\n'
    '"arquivo_rom": "cartucho" - utiliza o nome padrão "cartucho" como o nome das roms extraídas no\n'
    'ramdrive observe que a extensão do arquivo é mantida do arquivo original. Se arquivo_rom for ""\n'
    'entao o nome original do arquivo é mantido tendo apenas os espacos substituidos por "_".\n'
    '\n'
    '"abre_arquivador": "" - esta opção abre opcionalmente um arquivador (como winzip, winrar ou 7zFM)\n'
    'nas ocasiões que não foi possível encontrar nenhum tipo válido. Se o valor for "" exibe mensagem\n'
    'informando que não foi possível encontrar nenhum tipo válido e sai.\n'
    '\n'
    '"tam_ramdrive": "64M" - configura o ramdrive para o tamanho de 64mb, K ou G podem ser utilizados\n'
    'para especificar tamanhos variados de acordo com o tamanho das rom utilizadas.\n'
    '\n'
    '"format_ramdrive": "/fs:fat32 /q /y" - opcões para formatar a unidade assim que criada,\n'
    'infelizmente no momento essa funcionalidade está inoperante no windows 10 (e provávelmente em\n'
    'outras versões) devido as medidas de segurança que previnem que o dispositivo seja formatado,\n'
    'apresentando o diálogo do sistema para se formatar manualmente a unidade selecione então o tipo\n'
    'como FAT32 ou FAT o programa espera até um 30 segundos por padrão até que esta operação termine.\n'
    'Se os privilégios do usuário logado permitirem a formatação o comportamento esperado é que a\n'
    'unidade seja formatada automaticamente. Os argumentos aqui são os mesmo do comando format.\n'
    '\n'
    '"tempo_espera": 30 - tempo de espera máxima em segundos pela unidade ser formatada e ficar\n'
    'disponível.\n'
    '\n'
    '"tempo_espera_escolha": 10 - tempo de espera máxima em segundos em um menu de escolhas caso\n'
    'haja uma escolha padrão para aquele tipo.\n'
    '\n'
    'Descrição dos dados para adicionar um tipo novo:\n'
    '\n'
    'Exemplo com o tipo "Mega Drive":\n'
    '...\n'
    '"Mega Drive": {\n'
    ' "cmd": ["D:\\\\emul\\\\mega drive\\\\gens214\\\\x86\\\\gens.exe"],\n'
    ' "ext": ["bin", "smd", "md", "gen"],\n'
    ' "dos": false,\n'
    ' "extrai_tudo": false\n'
    '},\n'
    '...\n'
    '\n'
    '"Mega Drive" - Nome do tipo, o nome pode conter espaços. Se o nome começar com um * essa\n'
    'opção será utilizada como padrão para este tipo após o timeout da escolha. Apenas um deve ser\n'
    'marcado como padrão para comandos do mesmo tipo (se houver apenas um comando para este tipo\n'
    'não é necessário marcar ele como padrão).\n'
    '\n'
    '"cmd": ["D:\\\\emul\\\\mega drive\\\\gens214\\\\x86\\\\gens.exe"] - Caminho para o comando\n'
    'executado quando o tipo for encontrado, opções de linha de comando podem ser adicionadas com\n'
    'argumentos separados por vígulas, por exemplo:\n'
    '["C:\\\\Program Files (x86)\\\\DOSBox-0.74-3\\\\DOSBox.exe", "-fullscreen"].\n'
    '\n'
    'Os seguintes caracteres tem significado especial e podem ser usados como parte dos argumentos:\n'
    ' ?c - é substituído pelo nome e caminho completo do arquivo rom descompactado no ramdrive.\n'
    '   Exemplo: [..., "BRMSX -noenter -mapper 4 -ramslot 3 -diska ?c"]\n'
    ' ?d - é substituído pelo caminho relativo do arquivo rom descompactado no ramdrive.\n'
    '   Exemplo: [..., "-c", "cd ?d", "-c", "DOSSTART.BAT"]\n'
    ' ?D - é substituído pelo caminho completo do arquivo rom descompactado no ramdrive.\n'
    '   Exemplo: ["D:\\emul\\msx\\openmsx\\AMD64\\openmsx.exe", "-diska", "?D"]\n'
    'Se não for especificado nenhum dos caracteres especiais acima o nome e caminho completo da rom\n'
    'são adiciondos automaticamente como o último parâmetro de cmd amtes da execução do mesmo.\n'
    '\n'
    '"ext": ["bin", "smd", "md", "gen"] - Extensões conhecidas dos arquivos rom para o tipo\n'
    'determinado. Os arquivos rom são identificados primariamente pela extensão, quando uma rom tem\n'
    'seu tipo determinado pode ocorer de haver ambiguidades no caso de tipos diferentes utilizarem\n'
    'uma mesma extensão, nesse caso uma lista de opções é exibida listando as possibilidades encontradas.\n'
    'Opcionalmente pode-se especificar um nome de arquivo ao invés da extensão para melhor especificar\n'
    'os tipos, como no exemplo a seguir: "ext": ["dosgame.old"]\n'
    '\n'
    '"dos": false - se setada em true esta flag sinaliza que o programa a ser executado sofre as\n'
    'limitações de nome de arquivos comuns no dos e leva isso em consideração ao montar as linhas\n'
    'de comando adaptando os normes dos arquivos e diretórios para um tamanho maximo de 8 caracteres\n'
    'emulando o corpotamento do windows 95 que adicionava um final "~1" aos nomes longos encontrados.\n'
    '\n'
    '"extrai_tudo": false - Se setada em true esta flag sinaliza que todos os arquivo devem ser\n'
    'descomprimidos em um diretório temporário (acessível pelos caracteres especiais ?d ou ?D) no\n'
    'ramdrive ao invés de descomprimir apenas o arquivo rom com um nome e diretório temporário \n'
    '(acessível pelos caracteres ?c). Esta opção é útil em situações em que todos os arquivos devem\n'
    'estar presentes como quando imagens bin + cue ou bin + faixas de áudio compactadas são utilizadas\n'
    'ou quando um jogo de dos é executado via dosbox. Assim que a execução termina é realizado uma\n'
    'procura por arquivos novos e alterados, se nenhum for encontrado termina normalmente. Mas se forem\n'
    'encontrados arquivos novos ou alterados eles serão mostrados em uma lista. Futuramente eles serão\n'
    'salvos em um arquivo afim de persistir qualquer dado novo (como saves do jogador).\n'
    '\n'
    'Como criar um arquivo compactado para ser executado junto com o Dosbox:\n'
    '1 - Descompacte ou instale o jogo para um diretorio temporário.\n'
    '2 - Aplique qualquer crack ou patch necessário para rodar no dosbox.\n'
    '3 - Configure o suporte de som do jogo respeitando as opções ativas no dosbox.\n'
    '4 - Crie um arquivo bat chamado 00dosbox.bat (ou outro nome que deve ser configurado na chave\n'
    '    "alvos_prioritarios" em config.json e também "ext" para o tipo DOSBOX em dados_tipo.json) que\n'
    '    contém os comando necessários para iniciar o jogo e um exit opcional como ultimo comando (afim\n'
    '    de fechar a janela do dosbox automaticamentena). Este arquivo deve estar na raiz do diretório\n'
    '    do jogo.\n'
    '5 - Crie um arquivo comprimido usando algum formato suportado (recomendo 7z ou tar.xz) do\n'
    '    conteúdo do diretorio raiz do jogo (onde também deve estar o arquivo criado no passo 4).\n'
    '6 - Remove o diretorio temporário.\n'    
    'Agora você pode usar o arquivo compactado com o emu_rom_launcher para iniciar o dosbox!\n'
)


# cria o arquivo readme.txt no mesmo local do executavel do emu_rom_launcher
def cria_readme_txt():
    with open("readme.txt", "w") as readme_txt:
        # cria um texto
        readme_txt.write(description_text + "\n" + creditos_text[19 + len(VER):] +
                         "\n\nUtilização: emu_rom_launcher.exe [-h] [-r] caminho_arquivo\n\n" +
                         "O parâmetro -h exibe basicamente estas mesmas informações, -r " +
                         remove_text[:33].lower() + "\n" + remove_text[34:-1] +
                         " e caminho_arquivo é o " + caminho_text.lower()[:39] + "\n" +
                         caminho_text[40:76] + " " + caminho_text[77:132] + "\n" +
                         caminho_text[133:153] + " " + caminho_text[154:] + "\n\n" +
                         epilog_text)
