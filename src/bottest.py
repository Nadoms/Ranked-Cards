import asyncio
from os import getenv, path

import requests
import sys
from commands import card as carding
from commands import graph as graphing
from commands import match as matching
from commands import analysis as analysing
from gen_functions import games


async def main(command, name, type, season, match_id):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()
    response2 = requests.get(f"https://mcsrranked.com/api/matches/{match_id}").json()
    discord = "notnaddysalt"
    pfp = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"
    print(command, name, type)
    if command == "card":
        img = carding.main(name, response, discord, pfp, "grass.jpg")
    elif command == "plot":
        img = graphing.main(name, response, type, season)
    elif command == "match":
        img = matching.main(response2)
    elif command == "analysis":
        response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()[
            "data"
        ]
        detailed_matches = await games.get_detailed_matches(response, 0, 130)
        img1, img2 = analysing.main(response, detailed_matches)[2:4]
        img1.save("test.png")
        img2.save("test2.png")
        img1.show()
        img2.show()
        return
    else:
        return

    img.save("test.png")
    # img.show()


if __name__ == "__main__":
    command = "card"
    name = "Nadoms"
    season = 5
    type = "Completion time"
    match_id = 853645
    if len(sys.argv) >= 3:
        command = sys.argv[1]
        name = sys.argv[2]
        match_id = sys.argv[2]
    if len(sys.argv) >= 4:
        season = sys.argv[3]
    if len(sys.argv) >= 5:
        type = sys.argv[4]
    asyncio.run(main(command, name, type, season, match_id))
