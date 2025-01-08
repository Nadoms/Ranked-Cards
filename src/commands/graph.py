from datetime import datetime
import os

import requests
from PIL import Image

from graph_functions import add_graph, add_name, add_other, add_skin, add_stats
from gen_functions import games
from gen_functions.word import process_split


def main(name, response, data_type, season, matches):
    uuid = response["uuid"]

    then = datetime.now()
    file = add_graph.write(uuid, matches, data_type, season)
    if file == -1:
        return -1
    graph = Image.open(file)
    os.remove(file)
    then = process_split(then, "Drawing graph")
    add_name.write(graph, name)
    then = process_split(then, "Writing username")
    add_stats.write(graph, response)
    then = process_split(then, "Calculating stats")
    add_skin.write(graph, uuid)
    then = process_split(then, "Finding skin")
    add_other.write(graph)
    then = process_split(then, "Final touchups")

    return graph


if __name__ == "__main__":
    INPUT_NAME = "nadoms"
    RESPONSE = requests.get(
        f"https://mcsrranked.com/api/users/{INPUT_NAME}", timeout=10
    ).json()
    TYPE = "elo"
    SEASON = 5
    main(INPUT_NAME, RESPONSE, TYPE, SEASON).show()
