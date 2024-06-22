from os import path

def main():
    enters = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0
    }
    death_types = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0
    }
    deaths = 0
    resets = 0
    progress = 0
    total = 164049

    file = path.join("src", "database", "mcsrstats", "deaths.txt")
    prev_event = "ow"
    with open(file, "r") as f:

        while True:
            timeline = f.readline().strip().split(",")
            if not timeline[0]:
                break
            prev_event = "ow"
            enters["ow"] += 1
            for event in timeline:
                if event == "death":
                    death_types[prev_event] += 1
                    deaths += 1
                elif event == "reset":
                    death_types[prev_event] += 1
                    prev_event = "ow"
                    resets += 1
                elif event == "completed":
                    continue
                else:
                    enters[event] += 1
                    prev_event = event

            progress += 1
            if progress % 8192 == 0:
                print(f"{round(progress / total * 100, 1)}%!", end="\r")

    death_rates = {}
    for key in death_types:
        death_rates[key] = round(death_types[key] / enters["ow"], 2)

    print("Total games:", progress)
    print("Total deaths:", deaths, f"({round(deaths/progress, 2)} per game)")
    print("Total resets:", resets, f"({round(resets/progress, 2)} per game)")
    print("Death types:", death_types)
    print("Death rates:", death_rates)


if __name__ == "__main__":
    main()