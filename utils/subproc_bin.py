import subprocess

# Depois de muito sofrer com o bug do python ou do windows ou da biblioteca crt quem sabe
# o que eu seu eh que consigo ler assim entao virou meu metodo para sempre.
def run_and_get_retval_stdout(cmd):
    processo = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False
    )

    stdout, stderr = processo.communicate()
    return processo.returncode, stdout, stderr