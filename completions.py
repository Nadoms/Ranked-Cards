from src.comp_functions import add_graph

import requests
from PIL import Image
from os import path
from datetime import datetime

def __main__(name, response):
    if response["status"] != "error":
        response = response["data"]
        uuid = response["uuid"]
        file = path.join("src", "pics", "bgs", "end.jpg")
        card = Image.open(file)
        '''
        then = datetime.now()
        src.add_boxes.write(card, name, response)
        then = splits(then, 0)
        src.add_name.write(card, name, response)
        then = splits(then, 1)
        src.add_skin.write(card, uuid)
        then = splits(then, 4)
        src.add_other.write(card, name)
        then = splits(then, 8)'''
        return card
    else:
        print("Player not found.")

def splits(then, process):
    processes = ["Drawing boxes",
     "Writing username",
     "Calculating stats",
     "Pasting podium",
     "Finding skin",
     "Creating badge",
     "Averaging splits",
     "Getting socials",
     "Final touchups"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now

__main__("Nadoms", requests.get(f"https://mcsrranked.com/api/users/Nadoms").json()).show()