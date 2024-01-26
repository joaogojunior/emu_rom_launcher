from datetime import datetime
from subprocess import run as subproc_run
# Caminho para o script principal
scripts_compilar = ['emu_rom_launcher.py', 'detect_rom.py']

# Obtém a data e hora atual da compilação
data_hora_compilacao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
script_data_hora = 'emu_rom_launcher_build_date.py'
# Abre o arquivo emu_rom_launcher_build_date.py e adiciona a data/hora da compilação
with open(script_data_hora, 'w') as arquivo_script:
    arquivo_script.write('data_hora_build = "%s"\n' % data_hora_compilacao)

for script in scripts_compilar:
    # Comando PyInstaller para compilar o script principal
    subproc_run(
        ['pyinstaller', '--upx-dir=D:\\apps win32 e AMD64\\compactadores\\upx-4.2.2-win64', '--onefile', script]
    )
