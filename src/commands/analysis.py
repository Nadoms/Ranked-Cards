from datetime import datetime
from pathlib import Path

import requests

from analysis_functions import (
    bastion_insights,
    get_skin,
    get_comments,
    split_insights,
    ow_insights,
)
import rankedutils.constants
from rankedutils.word import process_split


def main(response, num_comps, detailed_matches, player_season, compare_season, rank_filter=None):
    uuid = response["uuid"]
    elo = response["seasonResult"]["last"]["eloRate"]
    if elo:
        elo = int(elo)

    then = datetime.now()
    skin = get_skin.main(uuid)
    then = process_split(then, "Finding skin")

    season_suffix = "" if compare_season == str(constants.SEASON) else f"_s{compare_season}"
    playerbase_file = Path("src") / "database" / f"playerbase{season_suffix}.json"
    general_comments = get_comments.main(
        response, detailed_matches, elo, player_season, compare_season, rank_filter, playerbase_file
    )
    then = process_split(then, "Generating insights")
    split_comm, split_polygon = split_insights.main(
        uuid, detailed_matches, elo, player_season, num_comps, rank_filter, playerbase_file
    )
    then = process_split(then, "Recognising split performance")
    ow_comm, ow_polygon = ow_insights.main(
        uuid, detailed_matches, rank_filter, playerbase_file
    )
    then = process_split(then, "Recognising OW performance")
    bastion_comm, bastion_polygon = bastion_insights.main(
        uuid, detailed_matches, elo, player_season, rank_filter, playerbase_file
    )
    then = process_split(then, "Recognising bastion performance")
    # polygons = combine.main(split_polygon, ow_polygon)

    comments = {
        "general": general_comments,
        "splits": split_comm,
        "ow": ow_comm,
        "bastion": bastion_comm,
    }

    return skin, comments, split_polygon, ow_polygon, bastion_polygon


if __name__ == "__main__":
    INPUT_NAME = "Nadoms"
    glob_response = requests.get(
        f"https://mcsrranked.com/api/users/{INPUT_NAME}", timeout=10
    ).json()
    main(glob_response).show()
