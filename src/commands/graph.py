from graph_functions import add_graph, add_name, add_other, add_skin

import requests
from PIL import Image
from os import path
from datetime import datetime

def main(name, response, type, season):
    if response["status"] == "error":
        print("Player not found.")
        return None
    response = response["data"]
    uuid = response["uuid"]

    then = datetime.now()
    file = add_graph.write(name, uuid, response, type, season)
    graph = Image.open(file)
    then = splits(then, 0)

    return graph

def splits(then, process):
    processes = ["Drawing graph",
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

'''if __name__ == "__main__":
    input_name = "nadoms"
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}").json()
    type = "elo"
    main(input_name, response, type)'''