from collections import deque
import csv
from datetime import datetime
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
CALLS_FILE = PROJECT_DIR / "database" / "calls_24.csv"
COMMON_FILE = PROJECT_DIR / "database" / "common.json"


def construct_player_list(length: int=500):
    print(f"\n***\nConstructing player list - {datetime.now()}\n***\n")
    with open(COMMON_FILE, "r") as f:
        player_list = json.load(f)
    player_list = {player: 0 for player in player_list}

    with open(CALLS_FILE, "r") as f:
        latest_calls = iter([f.readline()] + list(deque(f, maxlen=length)))

    reader = csv.DictReader(latest_calls)
    for row in reader:
        if (
            row["completed"] == "True"
            and row["command"] in ["card", "plot", "analysis"]
        ):
            if row["subject"] not in player_list:
                player_list[row["subject"]] = 0
            player_list[row["subject"]] += 1

    player_list = dict(
        sorted(player_list.items(), key=lambda item: item[1], reverse=True)
    )

    with open(COMMON_FILE, "w") as f:
        json.dump(player_list, f, indent=4)
    print(f"\n***\nPlayer List of {len(player_list)} Complete - {datetime.now()}\n***\n")

    return list(player_list.keys())


def get_player_list():
    with open(COMMON_FILE, "r") as f:
        player_list = json.load(f)
    return list(player_list.keys())
