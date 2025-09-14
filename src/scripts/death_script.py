import json
from os import path
import sys


def main(rank_no):
    enters = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0,
    }
    death_types = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0,
    }
    deaths = 0
    resets = 0
    progress = 0
    total = 164049

    input = path.join("src", "database", "mcsrstats", "deaths", f"deaths_{rank_no}.txt")
    output = path.join("src", "database", "mcsrstats", "deaths", "deaths.json")
    prev_event = "ow"
    with open(input, "r") as f:

        while True:
            timeline = f.readline().strip()
            if not timeline:
                break
            if timeline == "[]":
                continue

            good_timeline = tidy(timeline)

            prev_event = "ow"
            enters["ow"] += 1
            for event in good_timeline:
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
        death_rates[key] = round(death_types[key] / enters["ow"], 3)

    with open(output, "r") as f:
        ranked_death_rates = json.load(f)

    ranked_death_rates[str(rank_no)] = death_rates

    with open(output, "w") as f:
        deaths_json = json.dumps(ranked_death_rates, indent=4)
        f.write(deaths_json)

    print("Total games:", progress)
    print("Total deaths:", deaths, f"({round(deaths/progress, 2)} per game)")
    print("Total resets:", resets, f"({round(resets/progress, 2)} per game)")
    print("Death types:", death_types)
    print("Death rates:", death_rates)


def tidy(timeline):
    event_mapping = {
        "story.enter_the_nether": "nether",
        "nether.find_bastion": "bastion",
        "nether.find_fortress": "fortress",
        "projectelo.timeline.blind_travel": "blind",
        "story.follow_ender_eye": "stronghold",
        "story.enter_the_end": "end",
        "projectelo.timeline.death": "death",
        "projectelo.timeline.reset": "reset",
    }

    good_timeline = []

    if timeline[1:9] == "Timeline":
        timeline = timeline.split("),")
    elif timeline[1] == "'":
        timeline = timeline.split(",")

    for event in timeline:
        for type_key in event_mapping:
            if type_key in event:
                good_timeline.append(event_mapping[type_key])

    return good_timeline


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        rank_no = sys.argv[1]
    else:
        print("Usage: python death_script.py <rank_no>")
    main(rank_no)
