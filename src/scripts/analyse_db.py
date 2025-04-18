import json

from datetime import datetime
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(1, str(PROJECT_DIR))
from gen_functions import db, games
from models import train_model

SPLIT_MAPPING = {
    "story.enter_the_nether": "nether",
    "nether.find_bastion": "bastion",
    "nether.find_fortress": "fortress",
    "projectelo.timeline.blind_travel": "blind",
    "story.follow_ender_eye": "stronghold",
    "story.enter_the_end": "end",
}
OW_MAPPING = {
    "BURIED_TREASURE": "bt",
    "DESERT_TEMPLE": "dt",
    "RUINED_PORTAL": "rp",
    "SHIPWRECK": "ship",
    "VILLAGE": "village",
}


def main():
    print(f"\n***\nAnalysing database - {datetime.now()}\n***\n")
    season = games.get_season()
    completion_times = {}
    completion_nums = {}
    avg_sb_elo = {}
    split_times = {"ow": {}, "nether": {}, "bastion": {}, "fortress": {}, "blind": {}, "stronghold": {}, "end": {}}
    split_nums = {"ow": {}, "nether": {}, "bastion": {}, "fortress": {}, "blind": {}, "stronghold": {}, "end": {}}
    split_ranked = {"ow": [], "nether": [], "bastion": [], "fortress": [], "blind": [], "stronghold": [], "end": []}
    bastion_times = {"bridge": {}, "housing": {}, "stables": {}, "treasure": {}}
    bastion_nums = {"bridge": {}, "housing": {}, "stables": {}, "treasure": {}}
    bastion_ranked = {"bridge": [], "housing": [], "stables": [], "treasure": []}
    ow_times = {"bt": {}, "dt": {}, "rp": {}, "ship": {}, "village": {}}
    ow_nums = {"bt": {}, "dt": {}, "rp": {}, "ship": {}, "village": {}}
    ow_ranked = {"bt": [], "dt": [], "rp": [], "ship": [], "village": []}

    conn, cursor = db.start(PROJECT_DIR / "database" / "ranked.db")
    matches_info = db.query_db(
        cursor=cursor,
        items="id, seedType, bastionType, result_uuid, forfeited, time",
        season=season,
        type=2,
        decayed=False
    )
    for match_info in matches_info:
        match_id, seed_type, bastion_type, result_uuid, forfeited, result_time = match_info
        runs = db.query_db(
            cursor=cursor,
            table="runs",
            items="player_uuid, timeline",
            match_id=match_id,
        )

        for run in runs:
            uuid, timeline = run
            timeline = json.loads(timeline)
            curr_split = "ow"
            prev_time = 0
            bastion_entry = bastion_exit = 0

            for event in reversed(timeline):
                if event["type"] == "projectelo.timeline.reset":
                    prev_time = event["time"]
                    curr_split = "ow"
                    bastion_entry = bastion_exit = 0

                if event["type"] == "story.enter_the_nether":
                    ow_length = event["time"] - prev_time
                    if uuid not in ow_times[OW_MAPPING[seed_type]]:
                        ow_times[OW_MAPPING[seed_type]][uuid] = 0
                        ow_nums[OW_MAPPING[seed_type]][uuid] = 0
                    ow_times[OW_MAPPING[seed_type]][uuid] += ow_length
                    ow_nums[OW_MAPPING[seed_type]][uuid] += 1

                if event["type"] == "nether.find_bastion":
                    bastion_entry = event["time"]

                elif bastion_entry and not bastion_exit:
                    if event["type"] in [
                        "nether.find_fortress",
                        "projectelo.timeline.blind_travel",
                        "story.follow_ender_eye",
                        "story.enter_the_end",
                    ]:
                        bastion_exit = event["time"]
                        bastion_length = bastion_exit - bastion_entry
                        if uuid not in bastion_times[bastion_type.lower()]:
                            bastion_times[bastion_type.lower()][uuid] = 0
                            bastion_nums[bastion_type.lower()][uuid] = 0
                        bastion_times[bastion_type.lower()][uuid] += bastion_length
                        bastion_nums[bastion_type.lower()][uuid] += 1

                if event["type"] in SPLIT_MAPPING:
                    split_length = event["time"] - prev_time
                    if uuid not in split_times[curr_split]:
                        split_times[curr_split][uuid] = 0
                        split_nums[curr_split][uuid] = 0

                    split_times[curr_split][uuid] += split_length
                    split_nums[curr_split][uuid] += 1

                    prev_time = event["time"]
                    curr_split = SPLIT_MAPPING[event["type"]]

            if result_uuid == uuid and not forfeited:
                split_length = result_time - prev_time
                if uuid not in split_times[curr_split]:
                    split_times[curr_split][uuid] = 0
                    split_nums[curr_split][uuid] = 0
                split_times[curr_split][uuid] += split_length
                split_nums[curr_split][uuid] += 1

                if uuid not in completion_times:
                    completion_times[uuid] = 0
                    completion_nums[uuid] = 0
                completion_times[uuid] += result_time
                completion_nums[uuid] += 1

    full_elos = {}
    full_sbs = []

    completion_count = len(completion_times)
    for i, uuid in enumerate(completion_times):
        if i % (completion_count // 10) == 0:
            print(f"{i}/{completion_count}")
        elo = db.get_elo(cursor, uuid)
        sb = db.get_sb(cursor, uuid)
        if completion_nums[uuid] >= 5:
            avg_sb_elo[uuid] = {
                "avg": round(completion_times[uuid] / completion_nums[uuid]),
                "elo": elo,
                "sb": sb,
            }
        full_sbs.append((sb, elo))
        if elo:
            full_elos[uuid] = elo

    avgs = [(avg_sb_elo[uuid]["avg"], avg_sb_elo[uuid]["elo"]) for uuid in avg_sb_elo]
    elos = [avg_sb_elo[uuid]["elo"] for uuid in avg_sb_elo]
    sbs = [(avg_sb_elo[uuid]["sb"], avg_sb_elo[uuid]["elo"]) for uuid in avg_sb_elo]
    avgs = list(sorted(avgs, key=lambda item: item[0]))
    elos = list(sorted(elos, reverse=True))
    sbs = list(sorted(sbs, key=lambda item: item[0]))
    full_sbs = list(sorted(full_sbs, key=lambda item: item[0]))
    full_elos = dict(sorted(full_elos.items(), key=lambda item: item[1], reverse=True))
    full_elos_list = list(full_elos.values())

    for split in split_times:
        for uuid in split_times[split]:
            if split_nums[split][uuid] >= 3:
                split_ranked[split].append((
                    round(split_times[split][uuid] / split_nums[split][uuid]),
                    full_elos.get(uuid),
                ))
        split_ranked[split] = list(sorted(split_ranked[split], key=lambda item: item[0]))
        print(f"{split} count: {len(split_ranked[split])}")
    print()

    for bastion in bastion_times:
        for uuid in bastion_times[bastion]:
            if bastion_nums[bastion][uuid] >= 3:
                bastion_ranked[bastion].append((
                    round(bastion_times[bastion][uuid] / bastion_nums[bastion][uuid]),
                    full_elos.get(uuid),
                ))
        bastion_ranked[bastion] = list(sorted(bastion_ranked[bastion], key=lambda item: item[0]))
        print(f"{bastion} count: {len(bastion_ranked[bastion])}")
    print()

    for ow in ow_times:
        for uuid in ow_times[ow]:
            if ow_nums[ow][uuid] >= 3:
                ow_ranked[ow].append((
                    round(ow_times[ow][uuid] / ow_nums[ow][uuid]),
                    full_elos.get(uuid),
                ))
        ow_ranked[ow] = list(sorted(ow_ranked[ow], key=lambda item: item[0]))
        print(f"{ow} count: {len(ow_ranked[ow])}")

    playerbase_data = {
        "split": split_ranked,
        "bastion": bastion_ranked,
        "ow": ow_ranked,
        "avg": avgs,
        "elo": full_elos_list,
        "sb": full_sbs,
    }

    playerbase_file = PROJECT_DIR / "database" / "playerbase.json"
    with open(playerbase_file, "w") as f:
        json.dump(playerbase_data, f, indent=4)

    train_model.train(
        "avg",
        [(avg_elo[0] * 1e-6, avg_elo[1] * 1e-3) for avg_elo in avgs]
    )
    train_model.train(
        "sb",
        [(sb_elo[0] * 1e-6, sb_elo[1] * 1e-3) for sb_elo in sbs]
    )


if __name__ == "__main__":
    main()
