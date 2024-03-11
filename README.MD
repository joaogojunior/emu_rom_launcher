Emu_rom_launcher - tenta detectar o tipo de rom e executa o emulador apropiado.

O objetivo deste programa é descompactar um arquivo compactado em um diretorio
temporario criado em um ramdrive e executar um comando personalizado para abrir
este arquivo baseado no tipo do arquivo em questao.

Este programa é util como um atalho em sendto do windows, assim permitindo que
o explorer possa abrir qualquer arquivo com um emulador ou comando personalizado
dependendo do conteúdo ou extensão desse arquivo compactado.

Por exemplo, roms geralmente são armazenadas em arquivos .zip e tem alguns emuladores
(embora raros) que não suportem arquivos zip (como o NO$MSX, por exemplo.) no
windows explorer os arquivo zip geralmente já estão associados com o seu gerenciador
preferido como 7zFM mas colocando um atalho do emu_rom_launcher em sendto torna-se
possível enviar este arquivo zip para o emu_rom_laucher que gerencia o descomprimir
do arquivo em um local temporario no ramdrive, detecta o tipo do arquivo baseado no
seu conteudo e extensão e roda um comando para cada situação, como no exemplo dado,
se o zip conter um arquivo chamado arquivo.rom esse arquivo pode ser identificado
como uma rom MSX e chamar o emulador NO$MSX para abrir esse arquivo descomprimido,
removendo todos os arquivo após o uso.

Outra situação é executar jogos de DOS no DOSBOX direto do arquivo compactado,
nesse caso de uso o emu_rom_laucher é capaz de salvar e persistir as alterações que
ocorrem durante a execução do jogo, como quando um save ou o progresso é salvo.

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
