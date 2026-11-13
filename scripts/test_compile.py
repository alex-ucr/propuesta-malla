
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(cmd: list[str], *, cwd: Path) -> int:
    print(">", " ".join(cmd), flush=True)

    return subprocess.run(cmd, cwd=cwd).returncode

compila = ["python","compile_cursos_drivers.py", "--only", "Exploratoria"]

print(__file__)
print(ROOT)

print('*')

code = run(compila, cwd=ROOT)