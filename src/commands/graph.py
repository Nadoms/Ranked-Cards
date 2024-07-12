from datetime import datetime

import requests
from PIL import Image

from graph_functions import add_graph, add_name, add_other, add_skin, add_stats
from gen_functions import games

def main(name, response, data_type, season):
    response = response["data"]
    uuid = response["uuid"]

    then = datetime.now()
    matches = games.get_matches(response["nickname"], season, True)
    then = splits(then, 0)
    file = add_graph.write(uuid, matches, data_type, season)
    if file == -1:
        return -1
    then = splits(then, 1)
    graph = Image.open(file)
    add_name.write(graph, name)
    then = splits(then, 2)
    add_stats.write(graph, response)
    then = splits(then, 3)
    add_skin.write(graph, uuid)
    then = splits(then, 4)
    add_other.write(graph)
    then = splits(then, 5)

    return graph

def splits(then, process):
    processes = ["Gathering data",
                "Drawing graph",
                "Writing username",
                "Calculating stats",
                "Finding skin",
                "Final touchups"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now

if __name__ == "__main__":
    INPUT_NAME = "nadoms"
    RESPONSE = requests.get(f"https://mcsrranked.com/api/users/{INPUT_NAME}", timeout=10).json()
    TYPE = "elo"
    SEASON = 5
    main(INPUT_NAME, RESPONSE, TYPE, SEASON).show()
