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
