from pathlib import Path
import subprocess
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BOT = ROOT / "bot.py"
LOG = ROOT / "logs" / f"bot_{datetime.now().strftime('%m%d-%H%M')}.log"

process = subprocess.run(
    f"python3 -u {BOT} 2>&1 | tee {LOG}",
    text=True,
    shell=True,
)
