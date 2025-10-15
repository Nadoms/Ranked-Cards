import asyncio
import json

from datetime import datetime
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(1, str(PROJECT_DIR))
from rankedutils import constants, db
from models import train_model

SPLIT_MAPPING = {
    "story.enter_the_nether": "nether",
    "nether.find_bastion": "bastion",
    "nether.find_fortress": "fortress",
    "projectelo.timeline.blind_travel": "blind",
    "story.follow_ender_eye": "stronghold",
    "story.enter_the_end": "end",
}


def collect_matches(season, cursor):
    times = {
        "split": {"ow": {}, "nether": {}, "bastion": {}, "fortress": {}, "blind": {}, "stronghold": {}, "end": {}},
        "bastion": {"bridge": {}, "housing": {}, "stables": {}, "treasure": {}},
        "ow": {"bt": {}, "dt": {}, "rp": {}, "ship": {}, "village": {}},
        "completion": {},
    }
    nums = {
        "split": {"ow": {}, "nether": {}, "bastion": {}, "fortress": {}, "blind": {}, "stronghold": {}, "end": {}},
        "bastion": {"bridge": {}, "housing": {}, "stables": {}, "treasure": {}},
        "ow": {"bt": {}, "dt": {}, "rp": {}, "ship": {}, "village": {}},
        "completion": {},
    }
    runs_processed = 0

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

                # Dealing with overworlds
                if event["type"] == "story.enter_the_nether":
                    ow_length = event["time"] - prev_time
                    if uuid not in times["ow"][constants.OW_MAPPING[seed_type]]:
                        times["ow"][constants.OW_MAPPING[seed_type]][uuid] = 0
                        nums["ow"][constants.OW_MAPPING[seed_type]][uuid] = 0
                    times["ow"][constants.OW_MAPPING[seed_type]][uuid] += ow_length
                    nums["ow"][constants.OW_MAPPING[seed_type]][uuid] += 1

                # Dealing with bastions
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
                        if uuid not in times["bastion"][bastion_type.lower()]:
                            times["bastion"][bastion_type.lower()][uuid] = 0
                            nums["bastion"][bastion_type.lower()][uuid] = 0
                        times["bastion"][bastion_type.lower()][uuid] += bastion_length
                        nums["bastion"][bastion_type.lower()][uuid] += 1

                # Dealing with splits
                if event["type"] in SPLIT_MAPPING:
                    split_length = event["time"] - prev_time
                    if uuid not in times["split"][curr_split]:
                        times["split"][curr_split][uuid] = 0
                        nums["split"][curr_split][uuid] = 0

                    times["split"][curr_split][uuid] += split_length
                    nums["split"][curr_split][uuid] += 1

                    prev_time = event["time"]
                    curr_split = SPLIT_MAPPING[event["type"]]

            if result_uuid == uuid and not forfeited:
                split_length = result_time - prev_time
                if uuid not in times["split"][curr_split]:
                    times["split"][curr_split][uuid] = 0
                    nums["split"][curr_split][uuid] = 0
                times["split"][curr_split][uuid] += split_length
                nums["split"][curr_split][uuid] += 1

                if uuid not in times["completion"]:
                    times["completion"][uuid] = 0
                    nums["completion"][uuid] = 0
                times["completion"][uuid] += result_time
                nums["completion"][uuid] += 1

            runs_processed += 1

    return times, nums, runs_processed


async def analyse(season):
    print(f"\n***\nAnalysing database - {datetime.now()}\n***")
    ranked = {
        "split": {"ow": [], "nether": [], "bastion": [], "fortress": [], "blind": [], "stronghold": [], "end": []},
        "bastion": {"bridge": [], "housing": [], "stables": [], "treasure": []},
        "ow": {"bt": [], "dt": [], "rp": [], "ship": [], "village": []},
        "elo": [],
        "avg": [],
        "sb": []
    }

    conn, cursor = db.start(PROJECT_DIR / "database" / "ranked.db")
    print(f"\nCollecting runs - {datetime.now()}")
    times, nums, runs = collect_matches(season, cursor)
    print(f"Finished collecting {runs} runs")

    # Get the elo of every player accounted for
    print(f"\nFetching elos of {len(nums['split']['ow'])} players - {datetime.now()}")
    all_elos = {}
    for uuid in nums["split"]["ow"]:
        all_elos[uuid] = db.get_elo(cursor, uuid, season)
        await asyncio.sleep(0.001)

    training_data = {
        "avg": [],
        "sb": [],
    }

    # Construct training data and avg / sb ranking
    print(f"\nProcessing completions of {len(nums['completion'])} players - {datetime.now()}")
    for uuid in times["completion"]:
        elo = all_elos[uuid]
        avg = round(times["completion"][uuid] / nums["completion"][uuid])
        sb = db.get_sb(cursor, uuid, season)

        if not sb:
            print(uuid, sb, elo, nums["completion"])
        if elo:
            training_data["avg"].append((avg * 1e-6, elo * 1e-3))
            training_data["sb"].append((sb * 1e-6, elo * 1e-3))
            ranked["elo"].append(elo)

        if nums["completion"][uuid] >= 3:
            ranked["avg"].append((avg, elo, nums["completion"][uuid], uuid))

        ranked["sb"].append((sb, elo, uuid))
        await asyncio.sleep(0.001)

    ranked["elo"].sort(reverse=True)
    ranked["avg"] = sorted(ranked["avg"], key=lambda x: x[0])
    ranked["sb"] = sorted(ranked["sb"], key=lambda x: x[0])

    # Construct performance rankings
    for performance in ["split", "bastion", "ow"]:
        print(f"\nProcessing {performance}s - {datetime.now()}")
        for item in times[performance]:
            print(f"Processing {item} {performance}s of {len(nums[performance][item])} players...")
            for uuid in times[performance][item]:
                if nums[performance][item][uuid] >= 3:
                    item_avg = round(
                        times[performance][item][uuid]
                        / nums[performance][item][uuid]
                    )
                    ranked[performance][item].append(
                        (item_avg, all_elos[uuid], nums[performance][item][uuid], uuid)
                    )
            ranked[performance][item] = sorted(ranked[performance][item], key=lambda x: x[0])

    print(f"\nDumping insights into playerbase file - {datetime.now()}")
    playerbase_file = PROJECT_DIR / "database" / "playerbase.json"
    with open(playerbase_file, "w") as f:
        json.dump(ranked, f, indent=4)

    print(f"\nTraining models - {datetime.now()}")
    for data_oi in training_data:
        train_model.train(
            data_oi,
            training_data[data_oi]
        )
        await asyncio.sleep(1)

    conn.close()

    print(f"\n***\nAnalysis and Training Complete - {datetime.now()}\n***\n")


if __name__ == "__main__":
    asyncio.run(analyse(constants.SEASON))
