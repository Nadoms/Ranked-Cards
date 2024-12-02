from os import path

package = path.join("src")
import sys

sys.path.insert(1, package)
from gen_functions import word


def main():
    ordered_times = {"bridge": [], "housing": [], "stables": [], "treasure": []}

    for bastion_key in ordered_times:
        player_times = {}
        player_nums = {}
        file = path.join(
            "src", "database", "mcsrstats", "bastions", f"{bastion_key}.txt"
        )

        with open(file, "r") as f:
            while True:
                info = f.readline().strip().split()
                if not info:
                    break
                if info[0] == "<None>":
                    continue
                if info[2] == "Invalid":
                    continue
                if info[2][0] == "-":
                    continue
                if info[0] not in player_times.keys():
                    player_times[info[0]] = 0
                    player_nums[info[0]] = 0

                raw_time = word.get_raw_time(info[2])

                player_times[info[0]] += raw_time
                player_nums[info[0]] += 1

        for player_key in player_times:
            player_times[player_key] /= player_nums[player_key]
            if player_nums[player_key] >= 5:
                ordered_times[bastion_key].append(player_times[player_key])

        ordered_times[bastion_key].sort()

    file = path.join("src", "database", "mcsrstats", "bastion_splits.csv")
    with open(file, "w") as f:
        for i in range(len(ordered_times["bridge"])):
            line = ""
            for bastion_key in ordered_times:
                if i >= len(ordered_times[bastion_key]):
                    line += "FALSE"
                else:
                    line += str(int(ordered_times[bastion_key][i]))

                if bastion_key != "treasure":
                    line += ","
                else:
                    line += "\n"
            f.write(line)


if __name__ == "__main__":
    main()
