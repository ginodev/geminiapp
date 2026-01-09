# install_env.py
#
import os
import sys
import subprocess
from datetime import datetime

LOG_FILE = "logs/install_log.txt"
REQUIREMENTS_FILE = "requirements.txt"
VENV_PATH = ".venv"

def log(message):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{message}\n")
    print(message)

def run(cmd, description=None):
    if description:
        log(description)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        log(result.stdout.strip())
    if result.stderr.strip():
        log(result.stderr.strip())
    return result.returncode == 0

def package_installed(package_name):
    pip_exe = f"{VENV_PATH}\\Scripts\\pip.exe"
    result = subprocess.run(
        [pip_exe, "show", package_name],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def ensure_venv():
    if not os.path.exists(VENV_PATH):
        log("Creazione ambiente virtuale...")
        run(f"{sys.executable} -m venv {VENV_PATH}")
    else:
        log("Ambiente virtuale esistente, salto creazione...")

def upgrade_pip():
    log("Aggiornamento pip...")
    run(f"{VENV_PATH}\\Scripts\\python.exe -m pip install --upgrade pip")

def install_pytorch_stack():
    python_venv = f"{VENV_PATH}\\Scripts\\python.exe"
    torch_ok = package_installed("torch")
    torchaudio_ok = package_installed("torchaudio")
    torchvision_ok = package_installed("torchvision")

    if torch_ok and torchaudio_ok and torchvision_ok:
        log("✅ PyTorch stack già installato, salto...")
    else:
        log("🧩 Installazione PyTorch stack (CUDA 12.1)...")
        run([
            python_venv, "-m", "pip", "install", "--upgrade", "--no-cache-dir",
            "torch==2.5.1+cu121",
            "torchaudio==2.5.1+cu121",
            "torchvision==0.20.1+cu121",
            "--extra-index-url", "https://download.pytorch.org/whl/cu121"
        ], "Installazione PyTorch stack completata.")

def smart_install_requirements():
    pip_exe = f"{VENV_PATH}\\Scripts\\pip.exe"
    log("Controllo pacchetti mancanti o obsoleti...")

    run(f"{pip_exe} freeze > installed.txt")

    with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as reqs:
        requirements = [line.strip() for line in reqs if line.strip() and not line.startswith("#")]

    with open("installed.txt", "r", encoding="utf-8") as inst:
        installed = inst.read()

    to_install = []
    for req in requirements:
        pkg_name = req.split("==")[0].split(">=")[0].split("~=")[0].strip()
        if pkg_name.lower() not in installed.lower():
            to_install.append(req)

    if to_install:
        log(f"Pacchetti da installare o aggiornare: {to_install}")
        cmd = f"{pip_exe} install --upgrade --no-cache-dir {' '.join(to_install)}"
        run(cmd, "Installazione pacchetti mancanti/obsoleti completata.")
    else:
        log("✅ Tutti i pacchetti richiesti sono già aggiornati!")

def main():
    log("\n====== LOG INSTALLAZIONE ({}) ======".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    ensure_venv()
    upgrade_pip()
    install_pytorch_stack()
    smart_install_requirements()
    log("✅ Installazione completata!\n")

if __name__ == "__main__":
    main()