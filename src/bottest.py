import asyncio
from os import getenv, path

import argparse
import requests
import sys
from commands import card as carding
from commands import graph as graphing
from commands import match as matching
from commands import analysis as analysing
from gen_functions import api, constants, games, rank


DEFAULT_NAME = "Nadoms"
DEFAULT_ID = 1100002
DEFAULT_PLOT = "Completion time"
DEFAULT_DISCORD = "notnaddysalt"
DEFAULT_PFP = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"


async def card_command(args):
    response = api.User(args.name).get()
    history = api.UserMatches(name=args.name, type=2).get()
    return [carding.main(args.name, response, DEFAULT_DISCORD, DEFAULT_PFP, "grass.jpg", history)]


async def plot_command(args):
    response = api.User(args.name).get()
    matches = games.get_matches(args.name, args.season, True)
    return [graphing.main(args.name, response, args.type, args.season, matches)]


async def match_command(args):
    response = api.Match(args.id).get()
    return [matching.main(response)]


async def analysis_command(args):
    response = api.User(args.name).get()
    num_comps, detailed_matches = await games.get_detailed_matches(
        response, args.season, 5, 300
    )
    return analysing.main(
        response, num_comps, detailed_matches, args.season, args.rank_filter
    )[2:5]


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    card_parser = subparsers.add_parser("card", help="Generate a card")
    card_parser.add_argument("--name", type=str, help="Name of the player", default=DEFAULT_NAME)

    plot_parser = subparsers.add_parser("plot", help="Generate a plot")
    plot_parser.add_argument("--name", type=str, help="Name of the player", default=DEFAULT_NAME)
    plot_parser.add_argument("--season", type=int, help="Season number", default=constants.SEASON)
    plot_parser.add_argument("--type", type=str, help="Type of plot", default=DEFAULT_PLOT)

    match_parser = subparsers.add_parser("match", help="Generate a match image")
    match_parser.add_argument("--id", type=int, help="Match ID", default=DEFAULT_ID)

    analysis_parser = subparsers.add_parser("analysis", help="Perform analysis")
    analysis_parser.add_argument("--name", type=str, help="Name of the player", default=DEFAULT_NAME)
    analysis_parser.add_argument("--season", type=int, help="Season number", default=constants.SEASON)
    analysis_parser.add_argument("--rank_filter", type=rank.Rank, help="Ranks to compare to", default=None)

    args = parser.parse_args()

    command_map = {
        "card": card_command,
        "plot": plot_command,
        "match": match_command,
        "analysis": analysis_command,
    }

    for i, image in enumerate(asyncio.run(command_map[args.command](args))):
        image.save(f"test{i}.png")
        image.show()


if __name__ == "__main__":
    main()
