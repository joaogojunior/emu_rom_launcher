Emu_rom_launcher v0.1f - tenta detectar o tipo de rom e executa o emulador apropiado.
programado por joaogojunior@gmail.com e lançado em 29/12/2023 22:52:53

Utilização: emu_rom_launcher.exe [-h] [-r] caminho_arquivo

O parâmetro -h exibe basicamente estas mesmas informações, -r remove a unidade ramdrive ativa e
configurada em "caminho_temp_dir" e caminho_arquivo é o caminho para o arquivo rom sendo este o
argumento necessário para a operação normal. Arquivos compactados nos seguintes formatos são
suportados: .7z .zip .bz2 .gz .xz .tar .tar.bz2 .tar.gz .lzh .tar.xz e .lha.

Os caminhos e parâmetros dos emuladores devem ser configurados no arquivo dados_tipo.json.

Na plataforma windows todos os caminhos especificados nos arquivos de configuração e de tipos
devem conter "\\" (duplas barras) ao invés de "\" (apenas uma barra). Isso é devido ao caractere
"\" ter significados especiais no contexto dos ambientes utilizados e utilizando duplas barras torna
claro para o sistema que elas devem ser tratadas internamente como uma só barra quando for acessar os
arquivos evitando erros e ambiguidades.

Descrição das opções no arquivo config.json:

"caminho_temp_dir": "e:\\" - Utiliza unidade e: como unidade ramdrive temporária (imdisk deve ser
instalado previamente), certifique-se de escolher uma letra de unidade disponível caso já exista
uma unidade e:\ no seu computador.

"alvos_prioritarios": ["00dosbox.bat", "msxdos.sys"] - lista de alvos com prioridade de escolha sobre
os outros. Alvos mais a esquerda tem mais prioridade que um alvo mais a direita.

"arquivo_rom": "cartucho" - utiliza o nome padrão "cartucho" como o nome das roms extraídas no
ramdrive observe que a extensão do arquivo é mantida do arquivo original. Se arquivo_rom for ""
entao o nome original do arquivo é mantido tendo apenas os espacos substituidos por "_".

"abre_arquivador": "" - esta opção abre opcionalmente um arquivador (como winzip, winrar ou 7zFM)
nas ocasiões que não foi possível encontrar nenhum tipo válido. Se o valor for "" exibe mensagem
informando que não foi possível encontrar nenhum tipo válido e sai.

"tam_ramdrive": "64M" - configura o ramdrive para o tamanho de 64mb, K ou G podem ser utilizados
para especificar tamanhos variados de acordo com o tamanho das rom utilizadas.

"format_ramdrive": "/fs:fat32 /q /y" - opcões para formatar a unidade assim que criada,
infelizmente no momento essa funcionalidade está inoperante no windows 10 (e provávelmente em
outras versões) devido as medidas de segurança que previnem que o dispositivo seja formatado,
apresentando o diálogo do sistema para se formatar manualmente a unidade selecione então o tipo
como FAT32 ou FAT o programa espera até um 30 segundos por padrão até que esta operação termine.
Se os privilégios do usuário logado permitirem a formatação o comportamento esperado é que a
unidade seja formatada automaticamente. Os argumentos aqui são os mesmo do comando format.

"tempo_espera": 30 - tempo de espera máxima em segundos pela unidade ser formatada e ficar
disponível.

"tempo_espera_escolha": 10 - tempo de espera máxima em segundos em um menu de escolhas caso
haja uma escolha padrão para aquele tipo.

Descrição dos dados para adicionar um tipo novo:

Exemplo com o tipo "Mega Drive":
...
"Mega Drive": {
 "cmd": ["D:\\emul\\mega drive\\gens214\\x86\\gens.exe"],
 "ext": ["bin", "smd", "md", "gen"],
 "dos": false,
 "extrai_tudo": false
},
...

"Mega Drive" - Nome do tipo, o nome pode conter espaços. Se o nome começar com um * essa
opção será utilizada como padrão para este tipo após o timeout da escolha. Apenas um deve ser
marcado como padrão para comandos do mesmo tipo (se houver apenas um comando para este tipo
não é necessário marcar ele como padrão).

"cmd": ["D:\\emul\\mega drive\\gens214\\x86\\gens.exe"] - Caminho para o comando
executado quando o tipo for encontrado, opções de linha de comando podem ser adicionadas com
argumentos separados por vígulas, por exemplo:
["C:\\Program Files (x86)\\DOSBox-0.74-3\\DOSBox.exe", "-fullscreen"].

Os seguintes caracteres tem significado especial e podem ser usados como parte dos argumentos:
 ?c - é substituído pelo nome e caminho completo do arquivo rom descompactado no ramdrive.
   Exemplo: [..., "BRMSX -noenter -mapper 4 -ramslot 3 -diska ?c"]
 ?d - é substituído pelo caminho relativo do arquivo rom descompactado no ramdrive.
   Exemplo: [..., "-c", "cd ?d", "-c", "DOSSTART.BAT"]
 ?D - é substituído pelo caminho completo do arquivo rom descompactado no ramdrive.
   Exemplo: ["D:\emul\msx\openmsx\AMD64\openmsx.exe", "-diska", "?D"]
Se não for especificado nenhum dos caracteres especiais acima o nome e caminho completo da rom
são adiciondos automaticamente como o último parâmetro de cmd amtes da execução do mesmo.

"ext": ["bin", "smd", "md", "gen"] - Extensões conhecidas dos arquivos rom para o tipo
determinado. Os arquivos rom são identificados primariamente pela extensão, quando uma rom tem
seu tipo determinado pode ocorer de haver ambiguidades no caso de tipos diferentes utilizarem
uma mesma extensão, nesse caso uma lista de opções é exibida listando as possibilidades encontradas.
Opcionalmente pode-se especificar um nome de arquivo ao invés da extensão para melhor especificar
os tipos, como no exemplo a seguir: "ext": ["dosgame.old"]

"dos": false - se setada em true esta flag sinaliza que o programa a ser executado sofre as
limitações de nome de arquivos comuns no dos e leva isso em consideração ao montar as linhas
de comando adaptando os normes dos arquivos e diretórios para um tamanho maximo de 8 caracteres
emulando o corpotamento do windows 95 que adicionava um final "~1" aos nomes longos encontrados.

"extrai_tudo": false - Se setada em true esta flag sinaliza que todos os arquivo devem ser
descomprimidos em um diretório temporário (acessível pelos caracteres especiais ?d ou ?D) no
ramdrive ao invés de descomprimir apenas o arquivo rom com um nome e diretório temporário 
(acessível pelos caracteres ?c). Esta opção é útil em situações em que todos os arquivos devem
estar presentes como quando imagens bin + cue ou bin + faixas de áudio compactadas são utilizadas
ou quando um jogo de dos é executado via dosbox. Assim que a execução termina é realizado uma
procura por arquivos novos e alterados, se nenhum for encontrado termina normalmente. Mas se forem
encontrados arquivos novos ou alterados eles serão mostrados em uma lista. Futuramente eles serão
salvos em um arquivo afim de persistir qualquer dado novo (como saves do jogador).

Como criar um arquivo compactado para ser executado junto com o Dosbox:
1 - Descompacte ou instale o jogo para um diretorio temporário.
2 - Aplique qualquer crack ou patch necessário para rodar no dosbox.
3 - Configure o suporte de som do jogo respeitando as opções ativas no dosbox.
4 - Crie um arquivo bat chamado 00dosbox.bat (ou outro nome que deve ser configurado na chave
    "alvos_prioritarios" em config.json e também "ext" para o tipo DOSBOX em dados_tipo.json) que
    contém os comando necessários para iniciar o jogo e um exit opcional como ultimo comando (afim
    de fechar a janela do dosbox automaticamentena). Este arquivo deve estar na raiz do diretório
    do jogo.
5 - Crie um arquivo comprimido usando algum formato suportado (recomendo 7z ou tar.xz) do
    conteúdo do diretorio raiz do jogo (onde também deve estar o arquivo criado no passo 4).
6 - Remove o diretorio temporário.
Agora você pode usar o arquivo compactado com o emu_rom_launcher para iniciar o dosbox!
, este arquivo deve conter os comandos necessários para iniciá-lo )