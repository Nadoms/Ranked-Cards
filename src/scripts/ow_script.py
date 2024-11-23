from os import path

package = path.join("src", "gen_functions")
import sys

sys.path.insert(1, package)
import word


def main():
    ordered_times = {"bt": [], "dt": [], "rp": [], "ship": [], "village": []}

    for ow_key in ordered_times:
        player_times = {}
        player_nums = {}
        file = path.join("src", "database", "mcsrstats", "overworlds", f"{ow_key}.txt")

        with open(file, "r") as f:
            while True:
                info = f.readline().strip().split()
                if not info:
                    break
                elif info[0] == "<None>":
                    continue
                elif info[0] not in player_times.keys():
                    player_times[info[0]] = 0
                    player_nums[info[0]] = 0

                raw_time = word.get_raw_time(info[2])

                player_times[info[0]] += raw_time
                player_nums[info[0]] += 1

        for player_key in player_times:
            player_times[player_key] /= player_nums[player_key]
            ordered_times[ow_key].append(player_times[player_key])

    for ow_key in ordered_times:
        ordered_times[ow_key].sort()

    file = path.join("src", "database", "mcsrstats", "ow_splits.csv")
    with open(file, "w") as f:
        for i in range(len(ordered_times["village"])):
            line = ""
            for ow_key in ordered_times:
                if i >= len(ordered_times[ow_key]):
                    line += "FALSE"
                else:
                    line += str(int(ordered_times[ow_key][i]))

                if ow_key != "village":
                    line += ","
                else:
                    line += "\n"
            f.write(line)


if __name__ == "__main__":
    main()
