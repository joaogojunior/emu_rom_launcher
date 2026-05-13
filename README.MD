Emu_rom_launcher - tenta detectar o tipo de rom e executa o emulador apropiado.

O objetivo deste programa é extrair um arquivo compactado em um diretorio
temporario criado em ramdrive e executar o comando personalizado para abrir
este arquivo baseado no tipo do arquivo em questao.

Este programa é util como um atalho na pasta sendto do windows explorer, assim
permitindo que o explorer possa abrir qualquer arquivo com um emulador ou comando
personalizado dependendo do conteúdo ou extensão desse arquivo compactado.

Por exemplo, roms geralmente são armazenadas em arquivos como .zip e se desejar utilizar
com emuladores que não suportem esses formatos de arquivo (como o NO$MSX, que por exemplo
não suporta abrir direto do zip.), resta ao usuário o trabalho de abrir, descompactar,
escolher onde vai extrair, abrir o emulador e localizar o arquivo extraido no emulador. Mas
ao utilizar o emu_rom_launcher todo o trabalho se resume em clicar sobre o arquivo .zip da
rom desejada e selecionar com o botao direito "enviar para" (ou "send to") direcionando para
o emu_rom_launcher que automatiza todo o processo.

No windows explorer os arquivo zip geralmente já estão associados com o seu gerenciador
preferido como 7zFM mas atraves do uso de um atalho na pasta sendto torna-se possível enviar
este arquivo zip (ou outro formato suportado) para o emu_rom_laucher sem que seja necessario
associar tipos ou extensoes diferentes para o emu_rom_laucher ou ate mesmo o emulador em
questão.

O design customizavel do emu_rom_laucher permite customizar as ações no minimos detalhes,
suportando varios formatos de arquivos compactados. Ao descomprir um arquivo selecionado,
ele primeiro é extraido em um local temporario no ramdrive, tem seu tipo detectado baseado
no seu conteudo e nome de arquivo. Ao final roda um comando ja configurado para cada situação,
como no exemplo anterior, se o zip conter um arquivo chamado arquivo.rom esse arquivo sera
identificado como uma rom MSX pelo seu conteudo e ira chamar o emulador NO$MSX para abrir 
esse arquivo descomprimido, removendo todos os arquivos após o uso.

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

Arquivos compactados suportados no momento:
zip, 7z, lha, arj, gz, bz2, xz e tar.