from graph_functions import add_graph, add_name, add_other, add_skin, add_stats

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
    file = add_graph.write(uuid, response, type, season)
    if file == -1:
        return -1
    then = splits(then, 0)
    graph = Image.open(file)
    add_name.write(graph, name)
    then = splits(then, 1)
    add_stats.write(graph, uuid, response)
    then = splits(then, 2)
    add_skin.write(graph, uuid)
    then = splits(then, 4)
    add_other.write(graph)
    then = splits(then, 8)

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