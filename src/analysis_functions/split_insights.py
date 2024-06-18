from os import path
import numpy as np
import math
from PIL import Image, ImageDraw, ImagePath

def main(uuid, detailed_matches):
    average_splits = get_avg_splits(uuid, detailed_matches)
    ranked_splits = get_ranked_splits(average_splits)
    polygon = get_polygon(ranked_splits)

    return 0, 1

def get_avg_splits(uuid, detailed_matches):
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
        print(f"CHECKING MATCH {match['id']}")

        for event in reversed(match["timelines"]):
            if event["uuid"] != uuid:
                continue

            print(f"Checking event {event['type']}, currently in {prev_event} split.")

            if event["type"] == "projectelo.timeline.reset":
                prev_time = event["time"]
                prev_event = "ow"

            elif event["type"] in event_mapping.keys():
                split_length = event["time"] - prev_time
                print(f"New split detected, {event_mapping[event['type']]}! Last split took {split_length}")
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
        if len(splits_final_boss[key]) == 0:
            ranked_splits[key] = 0
        else:
            ranked_splits[key] = round(ranked_splits[key] / len(splits_final_boss[key]), 2)

    print(ranked_splits)
    return ranked_splits

def get_polygon(ranked_splits):
    sides = 5
    img_size = 720
    middle = img_size / 2
    init_prop = 1.2
    proportions = [init_prop, init_prop * 4/3, init_prop * 2, init_prop * 4, 10000]

    polygon_frame = Image.new("RGB", (img_size, img_size), "#313338")
    polygon = ImageDraw.Draw(polygon_frame)

    for proportion in proportions:
        polygon_size = middle * proportion
        xy = [ 
            ((math.cos(th) + proportion) * polygon_size, 
            (math.sin(th) + proportion) * polygon_size) 
            for th in [(i * (2 * math.pi) - 0.5 * math.pi) / sides for i in range(sides)] 
        ]
        if proportion == init_prop:
            polygon.polygon(xy, outline ="#ffffff", width=4)
        else:
            polygon.polygon(xy, outline ="#515358", width=3)

    for i in range(sides):
        polygon_size = middle * init_prop
        th = (i * (2 * math.pi) - 0.5 * math.pi) / sides
        xy = [(middle, middle),
            ((math.cos(th) + proportion) * polygon_size, 
            (math.sin(th) + proportion) * polygon_size)
        ]

    polygon_frame.show()

    return polygon