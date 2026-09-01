from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
BOT = ROOT / "bot.py"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

load_dotenv(ROOT.parent / ".env")


def main():
    subprocess.run(
        f"{sys.executable} -m pip uninstall rankedutils -y && {sys.executable} -m pip install git+https://github.com/Nadoms/ranked-utils.git",
        text=True,
        shell=True,
    )

    while True:
        log_path = LOG_DIR / f"bot_{datetime.now().strftime('%m%d-%H%M')}.log"
        process = subprocess.run(
            f"{sys.executable} -u {BOT} 2>&1 | tee {log_path}",
            text=True,
            shell=True,
        )

        print(f"Bot crashed ({process.returncode}). Restarting...")
        time.sleep(5)


if __name__ == "__main__":
    main()
