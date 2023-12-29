from os import getenv, path

import requests
import sys
from commands import card as carding
from commands import graph as graphing
from commands import analyse as analysing

def main(command, name, type, season, match_id):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()
    discord = "notnaddysalt"
    pfp = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"
    if command == "card":
        img = carding.main(name, response, discord, pfp)
        img.show()
    elif command == "graph":
        img = graphing.main(name, response, type, season)
        img.show()
    elif command == "analyse":
        array = analysing.main(name, match_id)
        for x in array:
            print(x)

if __name__ == "__main__":
    command = "analyse"
    name = "Nadoms"
    season = 3
    type = "Completion time"
    match_id = None
    if len(sys.argv) >= 3:
        command = sys.argv[1]
        name = sys.argv[2]
    if len(sys.argv) >= 4:
        season = sys.argv[3]
    if len(sys.argv) >= 5:
        type = sys.argv[4]
    main(command, name, type, season, match_id)