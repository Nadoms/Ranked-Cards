import asyncio
from os import getenv, path

import argparse
import requests
import sys
from commands import card as carding
from commands import graph as graphing
from commands import match as matching
from commands import analysis as analysing
from gen_functions import api, games


DEFAULT_NAME = "Nadoms"
DEFAULT_ID = 1100002
DEFAULT_PLOT = "Completion time"
DEFAULT_DISCORD = "notnaddysalt"
DEFAULT_PFP = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"


async def card_command(args):
    response = api.User(args.name).get()
    history = api.UserMatches(name=args.name, type=2).get()
    img = carding.main(args.name, response, DEFAULT_DISCORD, DEFAULT_PFP, "grass.jpg", history)
    img.save("test.png")


async def plot_command(args):
    response = api.User(args.name).get()
    matches = await games.get_matches(args.name, args.season, True)
    img = graphing.main(args.name, response, args.type, args.season, matches)
    img.save("test.png")


async def match_command(args):
    response = api.Match(args.id).get()
    img = matching.main(response)
    img.save("test.png")


async def analysis_command(args):
    response = api.User(args.name).get()
    num_comps, detailed_matches = await games.get_detailed_matches(
        response, args.season, 5, 300
    )
    img1, img2, img3 = analysing.main(
        response, num_comps, detailed_matches, args.season, args.rank_filter
    )[2:5]
    img1.save("test1.png")
    img2.save("test2.png")
    img3.save("test3.png")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    card_parser = subparsers.add_parser("card", help="Generate a card")
    card_parser.add_argument("--name", type=str, help="Name of the player", default=DEFAULT_NAME)

    plot_parser = subparsers.add_parser("plot", help="Generate a plot")
    plot_parser.add_argument("--name", type=str, help="Name of the player", default=DEFAULT_NAME)
    plot_parser.add_argument("--season", type=int, help="Season number", default=games.get_season())
    plot_parser.add_argument("--type", type=str, help="Type of plot", default=DEFAULT_PLOT)

    match_parser = subparsers.add_parser("match", help="Generate a match image")
    match_parser.add_argument("--id", type=int, help="Match ID", default=DEFAULT_ID)

    analysis_parser = subparsers.add_parser("analysis", help="Perform analysis")
    analysis_parser.add_argument("--name", type=str, help="Name of the player", default=DEFAULT_NAME)
    analysis_parser.add_argument("--season", type=int, help="Season number", default=games.get_season())
    analysis_parser.add_argument("--rank_filter", type=str, help="Ranks to compare to", default="All")

    args = parser.parse_args()

    command_map = {
        "card": card_command,
        "plot": plot_command,
        "match": match_command,
        "analysis": analysis_command,
    }

    asyncio.run(command_map[args.command](args))


if __name__ == "__main__":
    main()
