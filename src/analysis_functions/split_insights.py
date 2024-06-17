from os import path
import numpy as np

def main(detailed_matches):
    average_splits = get_avg_splits(detailed_matches)
    ranked_splits = get_ranked_splits(average_splits)
    penta_splits = get_penta_splits(ranked_splits)

    return 0, 1

def get_avg_splits(detailed_matches):
    number_splits = {
        "ow": 0, "nether": 0, "bastion": 0, "fortress": 0, "blind": 0, "stronghold": 0, "end": 0
    }
    total_splits = {
        "ow": 0, "nether": 0, "bastion": 0, "fortress": 0, "blind": 0, "stronghold": 0, "end": 0
    }
    average_splits = {
        "ow": 0,"nether": 0,"bastion": 0,"fortress": 0,"blind": 0,"stronghold": 0,"end": 0
    }
    event_mapping = {
        "story.enter_the_nether": "nether",
        "nether.find_bastion": "bastion",
        "nether.find_fortress": "fortress",
        "projectelo.timeline.blind_travel": "blind",
        "story.follow_ender_eye": "stronghold",
        "story.enter_the_end": "end"
    }

    for match in detailed_matches:
        if not match["timelines"]:
            continue
        
        prev_event = "ow"
        prev_time = 0

        for event in reversed(match["timelines"]):

            if event["type"] == "projectelo.timeline.reset":
                prev_time = event["time"]
                prev_event = "ow"

            elif event["type"] in event_mapping.keys():
                split_length = event["time"] - prev_time
                print(split_length)
                total_splits[prev_event] += split_length
                number_splits[prev_event] += 1

                prev_time = event["time"]
                prev_event = event_mapping[event["type"]]
    
    for key in average_splits:
        if number_splits[key] == 0:
            average_splits[key] = 0
        else:
            average_splits[key] = round(total_splits[key] / number_splits[key], 2)

    print(total_splits)
    print(average_splits)

    return average_splits

def get_ranked_splits(average_splits):
    ranked_splits = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0
    }
    splits_final_boss = {
        "ow": [],
        "nether": [],
        "bastion": [],
        "fortress": [],
        "blind": [],
        "stronghold": [],
        "end": []
    }

    file = path.join("src", "database", "mcsrstats", "ordered.csv")
    splits_index = ["ow", "nether", "bastion", "fortress", "blind", "stronghold", "end"]
    with open(file, "r") as f:

        while True:
            splits = f.readline().strip().split(",")
            if not splits[0]:
                break
            for i in range(6):
                if splits[i] != "FALSE":
                    splits_final_boss[splits_index[i]].append(int(splits[i]))

    for key in splits_final_boss:
        ranked_splits[key] = np.searchsorted(splits_final_boss[key], average_splits[key])

    print(ranked_splits)
    return ranked_splits

def get_penta_splits(detailed_matches):
    return []