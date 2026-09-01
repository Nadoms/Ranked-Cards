from pathlib import Path
import subprocess
import sys
from datetime import datetime

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
BOT = ROOT / "bot.py"
LOG = ROOT / "logs" / f"bot_{datetime.now().strftime('%m%d-%H%M')}.log"

load_dotenv(ROOT.parent / ".env")

subprocess.run(
    f"{sys.executable} -m pip uninstall rankedutils -y && {sys.executable} -m pip install git+https://github.com/Nadoms/ranked-utils.git",
    text=True,
    shell=True,
)

process = subprocess.run(
    f"{sys.executable} -u {BOT} 2>&1 | tee {LOG}",
    text=True,
    shell=True,
)
