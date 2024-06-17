from os import getenv, path

import requests
import sys
from commands import card as carding
from commands import graph as graphing
from commands import match as matching
from commands import analysis as analysing

def main(command, name, type, season, match_id):
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
        img = matching.main(response2, match_id)
    elif command == "analysis":
        img = analysing.main(response)
        
    img.save("test.png")
    img.show()

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
    main(command, name, type, season, match_id)