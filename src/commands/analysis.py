from datetime import datetime

import requests
import asyncio
from PIL import Image

from analysis_functions import get_skin, get_comments, split_insights, ow_insights
from gen_functions import games
from gen_functions.word import process_split


def main(response, num_comps, detailed_matches, season):
    uuid = response["uuid"]
    elo = response["seasonResult"]["last"]["eloRate"]
    if elo:
        elo = int(elo)

    split_polygon = Image.new("RGB", (400, 400), "#313338")
    ow_polygon = Image.new("RGB", (400, 400), "#313338")

    then = datetime.now()
    skin = get_skin.main(uuid)
    then = process_split(then, "Finding skin")
    general_comments = get_comments.main(response, elo, season)
    then = process_split(then, "Generating insights")
    split_comm, split_polygon = split_insights.main(
        uuid, detailed_matches, elo, season, num_comps
    )
    then = process_split(then, "Recognising split performance")
    ow_comm, ow_polygon = ow_insights.main(uuid, detailed_matches, season)
    then = process_split(then, "Recognising OW performance")
    # polygons = combine.main(split_polygon, ow_polygon)

    comments = {"general": general_comments, "splits": split_comm, "ow": ow_comm}

    return skin, comments, split_polygon, ow_polygon


if __name__ == "__main__":
    INPUT_NAME = "Nadoms"
    glob_response = requests.get(
        f"https://mcsrranked.com/api/users/{INPUT_NAME}", timeout=10
    ).json()
    main(glob_response).show()
