import asyncio
import json

from datetime import datetime
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(1, str(PROJECT_DIR))
from rankedutils import constants, db, insight
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
    }
    nums = {
        "split": {"ow": {}, "nether": {}, "bastion": {}, "fortress": {}, "blind": {}, "stronghold": {}, "end": {}},
        "bastion": {"bridge": {}, "housing": {}, "stables": {}, "treasure": {}},
        "ow": {"bt": {}, "dt": {}, "rp": {}, "ship": {}, "village": {}},
    }
    stats = {
        "elo": {},
        "peak": {},
        "sb": {},
        "games": {},
        "playtime": {},
        "wins": {},
        "draws": {},
        "losses": {},
        "forfeits": {},
        "cmptime": {},
        "completions": {},
        "chokes": {},
        "comebacks": {},
        "winwin": {},
        "lossloss": {},
    }
    last_ids = {}
    last_results = {}
    last_runs_processed = 0
    runs_processed = 0
    then = datetime.now()

    run_info = db.query_db(
        cursor=cursor,
        table="matches m",
        items=(
            "m.id, m.seedType, m.bastionType, m.result_uuid, m.forfeited, m.time,"
            "r.player_uuid, r.timeline, r.eloRate, r.change"
        ),
        join="runs r ON r.match_id = m.id",
        where=f"m.season = {season} AND m.type = 2 AND m.decayed = 0",
    )
    for run in run_info:
        if runs_processed % 50000 == 0:
            now = datetime.now()
            diff = (now - then).total_seconds()
            diff_processed = runs_processed - last_runs_processed
            print(f"{round(diff_processed / diff):>6} runs per second", end="\r")
            then = now
            last_runs_processed = runs_processed

        match_id, seed_type, bastion_type, result_uuid, forfeited, result_time, uuid, timeline, old_elo, change = run
        timeline = json.loads(timeline)
        curr_split = "ow"
        prev_time = 0
        bastion_entry = bastion_exit = 0
        choked = False
        won = result_uuid == uuid

        for event in reversed(timeline):
            if event["type"] == "projectelo.timeline.reset":
                prev_time = event["time"]
                curr_split = "ow"
                bastion_entry = bastion_exit = 0
                choked = True
            if event["type"] == "projectelo.timeline.death":
                choked = True

            # Dealing with overworlds
            if seed_type is not None:
                if event["type"] == "story.enter_the_nether":
                    ow_length = event["time"] - prev_time
                    if uuid not in times["ow"][constants.OW_MAPPING[seed_type]]:
                        times["ow"][constants.OW_MAPPING[seed_type]][uuid] = 0
                        nums["ow"][constants.OW_MAPPING[seed_type]][uuid] = 0
                    times["ow"][constants.OW_MAPPING[seed_type]][uuid] += ow_length
                    nums["ow"][constants.OW_MAPPING[seed_type]][uuid] += 1

            # Dealing with bastions
            if bastion_type is not None:
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

        if won and not forfeited:
            split_length = result_time - prev_time
            if uuid not in times["split"][curr_split]:
                times["split"][curr_split][uuid] = 0
                nums["split"][curr_split][uuid] = 0
            times["split"][curr_split][uuid] += split_length
            nums["split"][curr_split][uuid] += 1

            if uuid not in stats["completions"]:
                stats["cmptime"][uuid] = 0
                stats["completions"][uuid] = 0
                stats["sb"][uuid] = result_time
            stats["cmptime"][uuid] += result_time
            stats["completions"][uuid] += 1
            if result_time < stats["sb"][uuid]:
                stats["sb"][uuid] = result_time

        if uuid not in last_ids:
            last_ids[uuid] = 0
            last_results[uuid] = None
            stats["elo"][uuid] = None
            stats["peak"][uuid] = None
            stats["games"][uuid] = 0
            stats["playtime"][uuid] = 0
            stats["wins"][uuid] = 0
            stats["draws"][uuid] = 0
            stats["losses"][uuid] = 0
            stats["forfeits"][uuid] = 0
            stats["chokes"][uuid] = 0
            stats["comebacks"][uuid] = 0
            stats["winwin"][uuid] = 0
            stats["lossloss"][uuid] = 0
        if match_id > last_ids[uuid]:
            last_ids[uuid] = match_id
            stats["elo"][uuid] = old_elo + change if old_elo is not None else None

        if old_elo is not None and (
            stats["peak"][uuid] is None
            or old_elo + change > stats["peak"][uuid]
        ):
            stats["peak"][uuid] = old_elo + change
        stats["games"][uuid] += 1
        stats["playtime"][uuid] += result_time
        if won:
            stats["wins"][uuid] += 1
            if last_results[uuid] == "win":
                stats["winwin"][uuid] += 1
            last_results[uuid] = "win"
        elif result_uuid is None:
            stats["draws"][uuid] += 1
        else:
            stats["losses"][uuid] += 1
            if forfeited:
                stats["forfeits"][uuid] += 1
            if last_results[uuid] == "loss":
                stats["lossloss"][uuid] += 1
            last_results[uuid] = "loss"
        if choked:
            stats["chokes"][uuid] += 1
            if won:
                stats["comebacks"][uuid] += 1

        runs_processed += 1

    return times, nums, stats, runs_processed


async def analyse(season, filename="playerbase.json"):
    print(f"\n***\nAnalysing database (S{season}) - {datetime.now()}\n***")
    ranked = {
        "split": {"ow": [], "nether": [], "bastion": [], "fortress": [], "blind": [], "stronghold": [], "end": []},
        "bastion": {"bridge": [], "housing": [], "stables": [], "treasure": []},
        "ow": {"bt": [], "dt": [], "rp": [], "ship": [], "village": []},
        "stats": {
            "elo": [],
            "peak": [],
            "avg": [],
            "sb": [],
            "games": [],
            "playtime": [],
            "winrate": [],
            "ffl": [],
            "comprate": [],
            "chokerate": [],
            "resilience": [],
            "momentum": [],
            # "wins": [],
            # "draws": [],
            # "losses": [],
            # "forfeits": [],
            # "chokes": [],
            # "comebacks": [],
        }
    }

    conn, cursor = db.start(PROJECT_DIR / "database" / "ranked.db")
    print(f"\nCollecting runs - {datetime.now()}")
    times, nums, stats, runs = collect_matches(season, cursor)
    print(f"Finished collecting {runs} runs")

    training_data = {
        "avg": [],
        "sb": [],
    }

    # Construct training data and stat rankings
    print(f"\nProcessing matches of {len(stats['games'])} players - {datetime.now()}")
    for uuid in stats["games"]:
        elo = stats["elo"][uuid]
        if elo:
            ranked["stats"]["elo"].append(elo)
            ranked["stats"]["peak"].append((stats["peak"][uuid], elo, uuid))

        ranked["stats"]["games"].append((stats["games"][uuid], elo, uuid))
        ranked["stats"]["playtime"].append((stats["playtime"][uuid], elo, uuid))

        if stats["wins"][uuid] + stats["losses"][uuid] > 0:
            winrate = stats["wins"][uuid] / (stats["wins"][uuid] + stats["losses"][uuid])
            ranked["stats"]["winrate"].append((
                round(winrate, 3),
                elo,
                uuid,
                stats["wins"][uuid] + stats["losses"][uuid]
            ))
            if stats["wins"][uuid] + stats["losses"][uuid] > 1:
                ranked["stats"]["momentum"].append((
                    insight.calc_momentum(
                        stats["winwin"][uuid],
                        stats["lossloss"][uuid],
                        stats["wins"][uuid] + stats["losses"][uuid] - 1,
                        winrate,
                    ),
                    elo,
                    uuid,
                    stats["wins"][uuid] + stats["losses"][uuid] - 1
                ))
        if stats["losses"][uuid] > 0:
            ranked["stats"]["ffl"].append((
                round(stats["forfeits"][uuid] / stats["losses"][uuid], 3),
                elo,
                uuid,
                stats["losses"][uuid]
            ))
        ranked["stats"]["chokerate"].append((
            round(stats["chokes"][uuid] / stats["games"][uuid], 3),
            elo,
            uuid,
            stats["games"][uuid]
        ))
        if stats["chokes"][uuid] > 0:
            ranked["stats"]["resilience"].append((
                round(stats["comebacks"][uuid] / stats["chokes"][uuid], 3),
                elo,
                uuid,
                stats["chokes"][uuid]
            ))

        # Process completion related info
        if stats["completions"].get(uuid):
            avg = round(stats["cmptime"][uuid] / stats["completions"][uuid])
            sb = stats["sb"][uuid]

            if elo:
                training_data["avg"].append((avg * 1e-6, elo * 1e-3))
                training_data["sb"].append((sb * 1e-6, elo * 1e-3))

            if stats["completions"][uuid] >= 3:
                ranked["stats"]["avg"].append((avg, elo, uuid, stats["completions"][uuid]))

            ranked["stats"]["sb"].append((sb, elo, uuid))
            ranked["stats"]["comprate"].append((
                round(stats["completions"][uuid] / stats["games"][uuid], 3),
                elo,
                uuid,
                stats["completions"][uuid]
            ))

    ranked["stats"]["elo"].sort(reverse=True)
    for key in list(ranked["stats"].keys())[1:]:
        reverse = True
        if key in ("avg", "sb", "ffl", "chokerate"):
            reverse = False
        ranked["stats"][key].sort(key=lambda x: x[0], reverse=reverse)

    # Construct performance rankings
    for performance in ["split", "bastion", "ow"] if season >= 5 else ["split", "ow"]:
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
                        (item_avg, stats["elo"][uuid], uuid, nums[performance][item][uuid])
                    )
            ranked[performance][item] = sorted(ranked[performance][item], key=lambda x: x[0])

    print(f"\nDumping insights into playerbase file - {datetime.now()}")
    playerbase_file = PROJECT_DIR / "database" / filename
    with open(playerbase_file, "w") as f:
        json.dump(ranked, f, indent=4)

    print(f"\nTraining models - {datetime.now()}")
    for data_oi in training_data:
        filename = "models.json"
        if season != constants.SEASON:
            filename = f"models_s{season}.json"
        train_model.train(
            data_oi,
            training_data[data_oi],
            filename
        )
        await asyncio.sleep(1)

    conn.close()

    print(f"\n***\nAnalysis and Training Complete (S{season}) - {datetime.now()}\n***\n")


if __name__ == "__main__":
    asyncio.run(analyse(constants.SEASON))
