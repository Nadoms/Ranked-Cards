from os import path


def main():
    player_times = {}
    player_nums = {}
    ordered_times = {
        "ow": [],
        "nether": [],
        "bastion": [],
        "fortress": [],
        "blind": [],
        "stronghold": [],
        "end": [],
    }
    split_mapping = {
        "story.enter_the_nether": "ow",
        "nether.find_bastion": "nether",
        "nether.find_fortress": "bastion",
        "projectelo..blind_travel": "fortress",
        "story.follow_ender_eye": "blind",
        "story.enter_the_end": "stronghold",
        "rql.completed": "end",
    }
    event_mapping = {
        "story.enter_the_nether": "nether",
        "nether.find_bastion": "bastion",
        "nether.find_fortress": "fortress",
        "projectelo..blind_travel": "blind",
        "story.follow_ender_eye": "stronghold",
        "story.enter_the_end": "end",
        "rql.completed": "completed",
    }

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
                ordered_times[split_key].append(player_times[player_key][split_key])
            else:
                ordered_times[split_key].append(1000000000000)

    for split_key in ordered_times:
        ordered_times[split_key].sort()

    file = path.join("src", "database", "mcsrstats", "player_splits.csv")
    with open(file, "w") as f:
        for i in range(len(ordered_times["ow"])):
            line = ""
            for split_key in ordered_times:
                if ordered_times[split_key][i] == 1000000000000:
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
