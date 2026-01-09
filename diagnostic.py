import os
import sys
import time
import platform
import importlib
import subprocess
from datetime import datetime

# ────────────────────────────────────────────────
# COLORI TERMINALE (solo Windows e ANSI compatibili)
# ────────────────────────────────────────────────
class Color:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"

def print_section(title):
    print(f"\n{Color.CYAN}{'═' * 60}\n{Color.BOLD}{title}{Color.RESET}\n{'═' * 60}")

def check_module(name, import_name=None, min_version=None):
    """Controlla se un modulo è installato e opzionalmente la versione."""
    try:
        mod = importlib.import_module(import_name or name)
        version = getattr(mod, "__version__", "sconosciuta")
        print(f"{Color.GREEN}✅ {name}{Color.RESET} (versione: {version})")
        return True
    except Exception as e:
        print(f"{Color.RED}❌ {name}{Color.RESET} non disponibile → {e}")
        return False

# ────────────────────────────────────────────────
# 1️⃣ INFO BASE
# ────────────────────────────────────────────────
print_section("🔍 DIAGNOSTICA AMBIENTE - TRASCRIZIONE VOCALE AUTOMATICA")

print(f"{Color.BOLD}🧠 Sistema operativo:{Color.RESET} {platform.system()} {platform.release()}")
print(f"{Color.BOLD}🐍 Python versione:{Color.RESET} {sys.version.split()[0]}")
print(f"{Color.BOLD}📂 Directory di lavoro:{Color.RESET} {os.getcwd()}")

# ────────────────────────────────────────────────
# 2️⃣ VERIFICA TOKEN HUGGINGFACE
# ────────────────────────────────────────────────
print_section("🔑 Token Hugging Face")
token = os.getenv("HUGGINGFACE_TOKEN")
if token:
    print(f"{Color.GREEN}✅ Token trovato:{Color.RESET} {token[:10]}... (lunghezza: {len(token)})")
else:
    print(f"{Color.YELLOW}⚠️ Variabile HUGGINGFACE_TOKEN non impostata.{Color.RESET}")
    print("   Imposta con: setx HUGGINGFACE_TOKEN \"il_tuo_token\"")

# ────────────────────────────────────────────────
# 3️⃣ TEST MODULI PRINCIPALI
# ────────────────────────────────────────────────
print_section("📦 Verifica moduli installati")

modules = [
    "torch", "torchaudio", "whisperx", "pyannote.audio",
    "flask", "python-docx", "transformers", "librosa", "soundfile"
]

installed = [check_module(m.split(".")[0], m) for m in modules]

# ────────────────────────────────────────────────
# 4️⃣ TEST GPU TORCH
# ────────────────────────────────────────────────
print_section("⚙️ Verifica GPU (CUDA)")

try:
    import torch
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        print(f"{Color.GREEN}✅ GPU CUDA rilevata:{Color.RESET} {name}")
    else:
        print(f"{Color.YELLOW}⚠️ Nessuna GPU CUDA attiva. Uso CPU.{Color.RESET}")
except Exception as e:
    print(f"{Color.RED}❌ Errore test GPU:{Color.RESET} {e}")

# ────────────────────────────────────────────────
# 5️⃣ TEST CARICAMENTO WHISPERX
# ────────────────────────────────────────────────
print_section("🎙️ Test caricamento modello WhisperX")

try:
    import whisperx
    device = "cuda" if torch.cuda.is_available() else "cpu"
    start = time.time()
    model = whisperx.load_model("tiny", device=device, compute_type="float16" if device == "cuda" else "float32")
    duration = time.time() - start
    print(f"{Color.GREEN}✅ Modello WhisperX caricato correttamente in {duration:.2f}s su {device.upper()}.{Color.RESET}")
except Exception as e:
    print(f"{Color.RED}❌ Errore caricamento WhisperX:{Color.RESET} {e}")

# ────────────────────────────────────────────────
# 6️⃣ TEST CARICAMENTO PYANNOTE
# ────────────────────────────────────────────────
print_section("🧩 Test modello Pyannote.audio")

try:
    from pyannote.audio import Pipeline
    start = time.time()
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=token)
    duration = time.time() - start
    print(f"{Color.GREEN}✅ Modello Pyannote caricato in {duration:.2f}s{Color.RESET}")
except Exception as e:
    print(f"{Color.YELLOW}⚠️ Pyannote non disponibile o token mancante:{Color.RESET} {e}")

# ────────────────────────────────────────────────
# 7️⃣ STRUTTURA PROGETTO
# ────────────────────────────────────────────────
print_section("📁 Controllo struttura progetto")

folders = ["classes", "templates", "static", "logs", "uploads"]
files = ["server.py", "config.py", "requirements.txt", "run.bat"]

for f in folders:
    path = os.path.join(os.getcwd(), f)
    print(f"{Color.GREEN if os.path.isdir(path) else Color.RED}{'✅' if os.path.isdir(path) else '❌'} Cartella {f}{Color.RESET}")

for f in files:
    path = os.path.join(os.getcwd(), f)
    print(f"{Color.GREEN if os.path.isfile(path) else Color.RED}{'✅' if os.path.isfile(path) else '❌'} File {f}{Color.RESET}")

# ────────────────────────────────────────────────
# 8️⃣ TEST TORCH PERFORMANCE
# ────────────────────────────────────────────────
print_section("🔥 Test prestazioni Torch")

try:
    start = time.time()
    x = torch.rand((5000, 5000), device="cuda" if torch.cuda.is_available() else "cpu")
    y = torch.mm(x, x)
    print(f"{Color.GREEN}✅ Operazione Torch completata in {time.time() - start:.3f}s{Color.RESET}")
except Exception as e:
    print(f"{Color.YELLOW}⚠️ Operazione Torch fallita:{Color.RESET} {e}")

# ────────────────────────────────────────────────
# 9️⃣ RIASSUNTO FINALE
# ────────────────────────────────────────────────
print_section("🏁 DIAGNOSTICA COMPLETATA")

status = (
    f"{Color.GREEN}✅ Ambiente pronto all'uso{Color.RESET}"
    if all(installed)
    else f"{Color.YELLOW}⚠️ Alcuni moduli mancanti, esegui: pip install -r requirements.txt{Color.RESET}"
)
print(status)
print(f"{Color.CYAN}🕓 Ultimo controllo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.RESET}")
print("--------------------------------------------------")
