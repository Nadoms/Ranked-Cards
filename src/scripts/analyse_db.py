from os import path

package = path.join("src")
import sys
sys.path.insert(1, package)
from gen_functions import db, games

def main():
    season = games.get_season()
    split_times = {}
    split_nums = {}
    bastion_times = {}
    bastion_nums = {}
    ow_times = {}
    ow_nums = {}

    conn, cursor = db.start()
    match_ids = db.query_db(items="id", season=season)
    for match_id in match_ids:
        runs = db.query_db(
            table="runs",
            items="uuid, timeline",
            match_id=match_id,
        )

    for run in runs:
        uuid, timeline = run
        for event in timeline:
            pass

    file = path.join("src", "database", "mcsrstats", "cleaner_splits.txt")
    with open(file, "r") as f:
        while True:
            timeline = f.readline().strip().split(";")
            if not timeline[0]:
                break

            current_split = "ow"
            prev_time = 0

            for event in timeline:
                event = event.split(",")

                if event[2] not in player_times.keys():
                    player_times[event[2]] = {
                        "ow": 0,
                        "nether": 0,
                        "bastion": 0,
                        "fortress": 0,
                        "blind": 0,
                        "stronghold": 0,
                        "end": 0,
                    }
                    player_nums[event[2]] = {
                        "ow": 0,
                        "nether": 0,
                        "bastion": 0,
                        "fortress": 0,
                        "blind": 0,
                        "stronghold": 0,
                        "end": 0,
                    }

                if event[1] not in split_mapping.keys():
                    continue

                if split_mapping[event[1]] != current_split:
                    continue

                time = int(event[0]) - prev_time
                current_split = event_mapping[event[1]]
                prev_time = int(event[0])

                player_times[event[2]][split_mapping[event[1]]] += time
                player_nums[event[2]][split_mapping[event[1]]] += 1

    for player_key in player_times:
        for split_key in player_times[player_key]:
            if player_nums[player_key][split_key]:
                player_times[player_key][split_key] /= player_nums[player_key][
                    split_key
                ]
                if player_nums[player_key][split_key] >= 5:
                    ordered_times[split_key].append(player_times[player_key][split_key])

    for split_key in ordered_times:
        ordered_times[split_key].sort()

    file = path.join("src", "database", "mcsrstats", "player_splits.csv")
    with open(file, "w") as f:
        for i in range(len(ordered_times["ow"])):
            line = ""
            for split_key in ordered_times:
                if i >= len(ordered_times[split_key]):
                    line += "FALSE"
                else:
                    line += str(int(ordered_times[split_key][i]))

                if split_key != "end":
                    line += ","
                else:
                    line += "\n"
            f.write(line)


if __name__ == "__main__":
    main()
