Emu_rom_launcher v0.1f - tenta detectar o tipo de rom e executa o emulador apropiado.
programado por joaogojunior@gmail.com e lan�ado em 29/12/2023 22:52:53

Utiliza��o: emu_rom_launcher.exe [-h] [-r] caminho_arquivo

O par�metro -h exibe basicamente estas mesmas informa��es, -r remove a unidade ramdrive ativa e
configurada em "caminho_temp_dir" e caminho_arquivo � o caminho para o arquivo rom sendo este o
argumento necess�rio para a opera��o normal. Arquivos compactados nos seguintes formatos s�o
suportados: .7z .zip .bz2 .gz .xz .tar .tar.bz2 .tar.gz .lzh .tar.xz e .lha.

Os caminhos e par�metros dos emuladores devem ser configurados no arquivo dados_tipo.json.

Na plataforma windows todos os caminhos especificados nos arquivos de configura��o e de tipos
devem conter "\\" (duplas barras) ao inv�s de "\" (apenas uma barra). Isso � devido ao caractere
"\" ter significados especiais no contexto dos ambientes utilizados e utilizando duplas barras torna
claro para o sistema que elas devem ser tratadas internamente como uma s� barra quando for acessar os
arquivos evitando erros e ambiguidades.

Descri��o das op��es no arquivo config.json:

"caminho_temp_dir": "e:\\" - Utiliza unidade e: como unidade ramdrive tempor�ria (imdisk deve ser
instalado previamente), certifique-se de escolher uma letra de unidade dispon�vel caso j� exista
uma unidade e:\ no seu computador.

"alvos_prioritarios": ["00dosbox.bat", "msxdos.sys"] - lista de alvos com prioridade de escolha sobre
os outros. Alvos mais a esquerda tem mais prioridade que um alvo mais a direita.

"arquivo_rom": "cartucho" - utiliza o nome padr�o "cartucho" como o nome das roms extra�das no
ramdrive observe que a extens�o do arquivo � mantida do arquivo original. Se arquivo_rom for ""
entao o nome original do arquivo � mantido tendo apenas os espacos substituidos por "_".

"abre_arquivador": "" - esta op��o abre opcionalmente um arquivador (como winzip, winrar ou 7zFM)
nas ocasi�es que n�o foi poss�vel encontrar nenhum tipo v�lido. Se o valor for "" exibe mensagem
informando que n�o foi poss�vel encontrar nenhum tipo v�lido e sai.

"tam_ramdrive": "64M" - configura o ramdrive para o tamanho de 64mb, K ou G podem ser utilizados
para especificar tamanhos variados de acordo com o tamanho das rom utilizadas.

"format_ramdrive": "/fs:fat32 /q /y" - opc�es para formatar a unidade assim que criada,
infelizmente no momento essa funcionalidade est� inoperante no windows 10 (e prov�velmente em
outras vers�es) devido as medidas de seguran�a que previnem que o dispositivo seja formatado,
apresentando o di�logo do sistema para se formatar manualmente a unidade selecione ent�o o tipo
como FAT32 ou FAT o programa espera at� um 30 segundos por padr�o at� que esta opera��o termine.
Se os privil�gios do usu�rio logado permitirem a formata��o o comportamento esperado � que a
unidade seja formatada automaticamente. Os argumentos aqui s�o os mesmo do comando format.

"tempo_espera": 30 - tempo de espera m�xima em segundos pela unidade ser formatada e ficar
dispon�vel.

"tempo_espera_escolha": 10 - tempo de espera m�xima em segundos em um menu de escolhas caso
haja uma escolha padr�o para aquele tipo.

Descri��o dos dados para adicionar um tipo novo:

Exemplo com o tipo "Mega Drive":
...
"Mega Drive": {
 "cmd": ["D:\\emul\\mega drive\\gens214\\x86\\gens.exe"],
 "ext": ["bin", "smd", "md", "gen"],
 "dos": false,
 "extrai_tudo": false
},
...

"Mega Drive" - Nome do tipo, o nome pode conter espa�os. Se o nome come�ar com um * essa
op��o ser� utilizada como padr�o para este tipo ap�s o timeout da escolha. Apenas um deve ser
marcado como padr�o para comandos do mesmo tipo (se houver apenas um comando para este tipo
n�o � necess�rio marcar ele como padr�o).

"cmd": ["D:\\emul\\mega drive\\gens214\\x86\\gens.exe"] - Caminho para o comando
executado quando o tipo for encontrado, op��es de linha de comando podem ser adicionadas com
argumentos separados por v�gulas, por exemplo:
["C:\\Program Files (x86)\\DOSBox-0.74-3\\DOSBox.exe", "-fullscreen"].

Os seguintes caracteres tem significado especial e podem ser usados como parte dos argumentos:
 ?c - � substitu�do pelo nome e caminho completo do arquivo rom descompactado no ramdrive.
   Exemplo: [..., "BRMSX -noenter -mapper 4 -ramslot 3 -diska ?c"]
 ?d - � substitu�do pelo caminho relativo do arquivo rom descompactado no ramdrive.
   Exemplo: [..., "-c", "cd ?d", "-c", "DOSSTART.BAT"]
 ?D - � substitu�do pelo caminho completo do arquivo rom descompactado no ramdrive.
   Exemplo: ["D:\emul\msx\openmsx\AMD64\openmsx.exe", "-diska", "?D"]
Se n�o for especificado nenhum dos caracteres especiais acima o nome e caminho completo da rom
s�o adiciondos automaticamente como o �ltimo par�metro de cmd amtes da execu��o do mesmo.

"ext": ["bin", "smd", "md", "gen"] - Extens�es conhecidas dos arquivos rom para o tipo
determinado. Os arquivos rom s�o identificados primariamente pela extens�o, quando uma rom tem
seu tipo determinado pode ocorer de haver ambiguidades no caso de tipos diferentes utilizarem
uma mesma extens�o, nesse caso uma lista de op��es � exibida listando as possibilidades encontradas.
Opcionalmente pode-se especificar um nome de arquivo ao inv�s da extens�o para melhor especificar
os tipos, como no exemplo a seguir: "ext": ["dosgame.old"]

"dos": false - se setada em true esta flag sinaliza que o programa a ser executado sofre as
limita��es de nome de arquivos comuns no dos e leva isso em considera��o ao montar as linhas
de comando adaptando os normes dos arquivos e diret�rios para um tamanho maximo de 8 caracteres
emulando o corpotamento do windows 95 que adicionava um final "~1" aos nomes longos encontrados.

"extrai_tudo": false - Se setada em true esta flag sinaliza que todos os arquivo devem ser
descomprimidos em um diret�rio tempor�rio (acess�vel pelos caracteres especiais ?d ou ?D) no
ramdrive ao inv�s de descomprimir apenas o arquivo rom com um nome e diret�rio tempor�rio 
(acess�vel pelos caracteres ?c). Esta op��o � �til em situa��es em que todos os arquivos devem
estar presentes como quando imagens bin + cue ou bin + faixas de �udio compactadas s�o utilizadas
ou quando um jogo de dos � executado via dosbox. Assim que a execu��o termina � realizado uma
procura por arquivos novos e alterados, se nenhum for encontrado termina normalmente. Mas se forem
encontrados arquivos novos ou alterados eles ser�o mostrados em uma lista. Futuramente eles ser�o
salvos em um arquivo afim de persistir qualquer dado novo (como saves do jogador).

Como criar um arquivo compactado para ser executado junto com o Dosbox:
1 - Descompacte ou instale o jogo para um diretorio tempor�rio.
2 - Aplique qualquer crack ou patch necess�rio para rodar no dosbox.
3 - Configure o suporte de som do jogo respeitando as op��es ativas no dosbox.
4 - Crie um arquivo bat chamado 00dosbox.bat (ou outro nome que deve ser configurado na chave
    "alvos_prioritarios" em config.json e tamb�m "ext" para o tipo DOSBOX em dados_tipo.json) que
    cont�m os comando necess�rios para iniciar o jogo e um exit opcional como ultimo comando (afim
    de fechar a janela do dosbox automaticamentena). Este arquivo deve estar na raiz do diret�rio
    do jogo.
5 - Crie um arquivo comprimido usando algum formato suportado (recomendo 7z ou tar.xz) do
    conte�do do diretorio raiz do jogo (onde tamb�m deve estar o arquivo criado no passo 4).
6 - Remove o diretorio tempor�rio.
Agora voc� pode usar o arquivo compactado com o emu_rom_launcher para iniciar o dosbox!
, este arquivo deve conter os comandos necess�rios para inici�-lo )