import asyncio
from io import BytesIO
import math
import nextcord
import json
from nextcord import File, Interaction, SlashOption, Embed
from nextcord.ext import commands
from os import getenv, path
from dotenv import load_dotenv
from time import time
import traceback

from commands import (
    card as carding,
    graph as graphing,
    match as matching,
    analysis as analysing,
    race as racing,
    leaderboard as leading,
)
from gen_functions import games, api, rank, constants, word
from gen_functions.numb import digital_time
from scripts import analyse_db, construct_players, load_matches

START_ID = 2118500
TESTING_MODE = True
ALL_SEASONS = [str(season) for season in range(1, constants.SEASON + 1)]
ALL_COUNTRIES = [country for country in leading.COUNTRY_MAPPING]
API_COOLDOWN_MSG = "Too many commands have been issued! The Ranked API is cooling down... (~10 mins)"
GENERIC_ERROR_MSG = "An error has occurred. <@298936021557706754> fix it pls:"
token = "TEST_TOKEN" if TESTING_MODE else "DISCORD_TOKEN"
default_guild_ids = [735859906434957392] if TESTING_MODE else None
player_list = []

intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(
    command_prefix="=",
    intents=intents,
    default_guild_ids=default_guild_ids,
)


class Topics(nextcord.ui.View):
    def __init__(self, interaction, embeds, images):
        super().__init__(timeout=840)
        self.value = None
        self.interaction = interaction
        self.general_embed = embeds[0]
        self.topic_embeds = embeds[1:]
        self.images = images

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, nextcord.ui.Button):
                item.style = nextcord.ButtonStyle.grey
                item.disabled = True
        await self.interaction.edit_original_message(view=self)
        for image in self.images:
            image.close()

    def set_embed_image(self, embed, image):
        file = image_to_file(image, f"{self.value}.png", close=False)
        embed.set_image(url=f"attachment://{self.value}.png")
        return file

    @nextcord.ui.button(label="Splits", style=nextcord.ButtonStyle.blurple)
    async def show_splits(
        self,
        button: nextcord.ui.Button,
        interaction: Interaction,
    ):
        print(f"Flipping to splits for {interaction.user.name}")
        self.value = "splits"
        file = self.set_embed_image(self.topic_embeds[0], self.images[0])
        await self.interaction.edit_original_message(
            embeds=[self.general_embed, self.topic_embeds[0]],
            file=file,
        )
        self._View__timeout_expiry -= self.timeout

    @nextcord.ui.button(label="Bastions", style=nextcord.ButtonStyle.gray)
    async def show_bastions(
        self,
        button: nextcord.ui.Button,
        interaction: Interaction,
    ):
        print(f"Flipping to bastions for {interaction.user.name}")
        self.value = "bastions"
        file = self.set_embed_image(self.topic_embeds[1], self.images[1])
        await self.interaction.edit_original_message(
            embeds=[self.general_embed, self.topic_embeds[1]],
            file=file,
        )
        self._View__timeout_expiry -= self.timeout

    @nextcord.ui.button(label="Overworlds", style=nextcord.ButtonStyle.green)
    async def show_overworlds(
        self,
        button: nextcord.ui.Button,
        interaction: Interaction,
    ):
        print(f"Flipping to overworlds for {interaction.user.name}")
        self.value = "ows"
        file = self.set_embed_image(self.topic_embeds[2], self.images[2])
        await self.interaction.edit_original_message(
            embeds=[self.general_embed, self.topic_embeds[2]],
            file=file,
        )
        self._View__timeout_expiry -= self.timeout


class LBPage(nextcord.ui.View):
    def __init__(self, interaction: Interaction, embeds: list):
        super().__init__(timeout=840)
        self.interaction = interaction
        self.embeds = embeds
        self.size = len(embeds)
        self.page = 0

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, nextcord.ui.Button):
                item.style = nextcord.ButtonStyle.grey
                item.disabled = True
        await self.interaction.edit_original_message(view=self)

    @nextcord.ui.button(label="Previous", style=nextcord.ButtonStyle.blurple)
    async def previous(
        self,
        button: nextcord.ui.Button,
        interaction: Interaction,
    ):
        self.page = (self.page - 1) % self.size
        await self.update(interaction)

    @nextcord.ui.button(label="Next", style=nextcord.ButtonStyle.blurple)
    async def next(
        self,
        button: nextcord.ui.Button,
        interaction: Interaction,
    ):
        self.page = (self.page + 1) % self.size
        await self.update(interaction)

    async def update(
        self,
        interaction: Interaction,
    ):
        print(f"Flipping to page {self.page} for {interaction.user.name}")
        await self.interaction.edit_original_message(embeds=[self.embeds[self.page]])
        self._View__timeout_expiry -= self.timeout


class MatchAgo(nextcord.ui.View):
    def __init__(
        self,
        interaction: Interaction,
        matches: list[dict],
        input_uuid: str,
    ):
        super().__init__(timeout=840)
        self.interaction = interaction
        self.charts = []
        self.input_uuid = input_uuid
        self.names = []
        self.ids = []
        self.name_matches(matches[:25])
        self.matches_seen = [0]
        self.select = nextcord.ui.Select(
                placeholder="Select a match...",
                options=[
                    nextcord.SelectOption(label=name, value=str(self.ids[i]))
                    for i, name in enumerate(self.names)
                ],
            )
        self.select.callback = self.select_match
        self.add_item(
            self.select
        )

    def name_matches(self, matches):
        self.ids = [match["id"] for match in matches]
        for i, match in enumerate(matches):
            duration = match["result"]["time"]
            forfeited = match["forfeited"]
            won = match["result"]["uuid"] == self.input_uuid
            days_ago = word.get_ago(match["date"])
            opponent = next(
                player["nickname"]
                for player in match["players"]
                if player["uuid"].lower() != self.input_uuid.lower()
            )
            self.names.append(
                f"{(i + 1):2d}. {'🏆' if won else '🥀'}"
                f"{'🏳️' if forfeited else ' ' + digital_time(duration)} vs {opponent} "
                f"({days_ago})"
            )

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, nextcord.ui.Button):
                item.style = nextcord.ButtonStyle.grey
                item.disabled = True
        await self.interaction.edit_original_message(view=self)

    async def select_match(
        self,
        interaction: Interaction,
    ):
        selected_id = int(self.select.values[0])
        print(f"Switching to match {selected_id} for {interaction.user.name}")

        response = api.Match(id=selected_id).get()
        await interaction.response.defer()
        img = matching.main(response)

        file = image_to_file(img, f"chart_{selected_id}.png")
        await self.interaction.edit_original_message(file=file)
        self._View__timeout_expiry -= self.timeout


@bot.event
async def on_ready():
    print("Bot is running")


# SLASH COMMANDS
@bot.slash_command(name="ping", description="Pong!")
async def ping(interaction: Interaction):
    await interaction.response.send_message("Pong!")


@bot.slash_command(
    name="card", description="Generates a card for the player you specify."
)
async def card(
    interaction: Interaction,
    input_name: str = SlashOption(
        "name",
        required=False,
        description="The player to generate a card for.",
        default="",
    ),
):
    connected = False
    if not input_name:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message(
                "Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a minecraft username.",
            )
            update_records(interaction, "card", "Unknown", False)
            return
        connected = True

    async def fail_get(msg):
        await interaction.response.send_message(msg)
        update_records(interaction, "card", input_name, False)

    print(f"---\nGenerating card for {input_name}")
    try:
        response = api.User(name=input_name).get()

    except api.APINotFoundError as e:
        print(e)
        not_found = f"Player not found (`{input_name}`)."
        if connected:
            await fail_get(f"{not_found} Connect to your new Minecraft username with </connect:1149442234513637448>.")
            return
        await fail_get(not_found)
        return

    except api.APIRateLimitError as e:
        print(e)
        await fail_get(API_COOLDOWN_MSG)
        return

    await interaction.response.defer()

    input_name = response["nickname"]
    uid, background = get_user_info(response, input_name)
    user = await bot.fetch_user(uid)
    pfp = user.avatar
    if not pfp:
        pfp = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"
    discord = str(user)
    if discord[-2:] == "#0":
        discord = discord[:-2]

    history = api.UserMatches(name=input_name, type=2).get()

    try:
        img = carding.main(input_name, response, discord, pfp, background, history)
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(f"{GENERIC_ERROR_MSG}\n```{traceback.format_exc()}```")
        update_records(interaction, "card", input_name, False)
        return

    file = image_to_file(img, f"card_{input_name}.png")
    await interaction.followup.send(file=file)
    update_records(interaction, "card", input_name, True)


@bot.slash_command(
    name="plot",
    description="Illustrates a graph for the player + metric that you choose.",
)
async def plot(
    interaction: Interaction,
    input_name: str = SlashOption(
        "name",
        required=False,
        description="The player to draw a graph for.",
        default="",
    ),
    type: str = SlashOption(
        "type",
        required=False,
        description="The metric to plot.",
        default="Elo",
        choices=["Elo", "Completion time"],
    ),
    season: str = SlashOption(
        "season",
        required=False,
        description="The season to gather data for.",
        default=str(constants.SEASON),
        choices=ALL_SEASONS + ["Lifetime"],
    ),
):
    connected = False
    if not input_name:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message(
                "Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a minecraft username.",
            )
            update_records(interaction, "plot", "Unknown", False)
            return
        connected = True

    async def fail_get(msg):
        await interaction.response.send_message(msg)
        update_records(interaction, "plot", input_name, False)

    print(f"---\nDrawing {type} graph for {input_name}")
    try:
        response = api.User(name=input_name).get()

    except api.APINotFoundError as e:
        print(e)
        not_found = f"Player not found (`{input_name}`)."
        if connected:
            await fail_get(f"{not_found} Connect to your new Minecraft username with </connect:1149442234513637448>.")
            return
        await fail_get(not_found)
        return

    except api.APIRateLimitError as e:
        print(e)
        await fail_get(API_COOLDOWN_MSG)
        return

    await interaction.response.defer()

    input_name = response["nickname"]
    matches = games.get_matches(response["nickname"], season, True)

    try:
        img = graphing.main(input_name, response, type, season, matches)
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(f"{GENERIC_ERROR_MSG}\n```{traceback.format_exc()}```")
        update_records(interaction, "plot", input_name, False)
        return

    if img == -1:
        if type == "Elo":
            msg1 = "games played"
        elif type == "Completion time":
            msg1 = "completed matches"
        if season != "Lifetime":
            msg2 = f" from season {season}"
        else:
            msg2 = ""
        await interaction.followup.send(f"`{input_name}` has not enough {msg1}{msg2}.")
        update_records(interaction, "plot", input_name, False)
        return

    file = image_to_file(img, f"graph_{input_name}.png")
    await interaction.followup.send(file=file)
    update_records(interaction, "plot", input_name, True)


@bot.slash_command(
    name="match",
    description="Produces a chart on your most recent match, or the match specified.",
)
async def match(
    interaction: Interaction,
    match_id: str = SlashOption(
        "match_id",
        required=False,
        description="The specific match ID to draw a chart of.",
        default=None,
    ),
):
    view = nextcord.utils.MISSING
    if not match_id:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message(
                "Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a match ID.",
            )
            update_records(interaction, "match", "Unknown", False)
            return

        print(f"---\nFinding {input_name}'s last match")
        try:
            recent_matches = api.UserMatches(
                name=input_name, count=25, type=2, excludedecay=True
            ).get()
        except api.APIRateLimitError as e:
            print(e)
            await interaction.response.send_message(API_COOLDOWN_MSG)
            update_records(interaction, "match", "Unknown", False)
            return

        if recent_matches == []:
            await interaction.response.send_message(
                f"Player has no matches from this season. ({input_name})"
            )
            update_records(interaction, "match", "Unknown", False)
            return

        match_id = recent_matches[0]["id"]

        input_uuid = next(
            player["uuid"]
            for player in recent_matches[0]["players"]
            if player["nickname"].lower() == input_name.lower()
        )
        view = MatchAgo(
            interaction,
            recent_matches,
            input_uuid,
        )

    async def fail_get(msg):
        await interaction.response.send_message(msg)
        update_records(interaction, "match", match_id, False)

    print(f"---\nCharting match {match_id}")
    try:
        response = api.Match(id=match_id).get()
    except api.APINotFoundError as e:
        print(e)
        await fail_get(f"Match not found (`{match_id}`).")
        return
    except api.APIRateLimitError as e:
        print(e)
        await fail_get(API_COOLDOWN_MSG)
        return

    if response["type"] >= 3 or response["decayed"] == True:
        await interaction.response.send_message(
            f"Match must be a ranked or casual game. (`{match_id}`)"
        )
        update_records(interaction, "match", match_id, False)
        return

    await interaction.response.defer()

    try:
        img = matching.main(response)
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(f"{GENERIC_ERROR_MSG}\n```{traceback.format_exc()}```")
        update_records(interaction, "match", match_id, False)
        return

    file = image_to_file(img, f"chart_{match_id}.png")
    await interaction.followup.send(file=file, view=view)
    update_records(interaction, "match", match_id, True)


@bot.slash_command(
    name="analysis",
    description="Analyses past games to visualise how a player performs throughout their runs.",
)
async def analysis(
    interaction: Interaction,
    input_name: str = SlashOption(
        "name",
        required=False,
        description="The player to analyse.",
        default="",
        autocomplete=True,
    ),
    season: str = SlashOption(
        "season",
        required=False,
        description="The season to gather data from.",
        default=str(constants.SEASON),
        choices=ALL_SEASONS,
    ),
    selection: str = SlashOption(
        "selection",
        required=False,
        description="How many matches to select for analysis. Lower sample size means lower confidence.",
        default="Last 300",
        choices=[
            "Last 1000",
            "Last 300",
            "Last 100",
            "Last 50",
        ],
    ),
    rank_filter: str = SlashOption(
        "rank_filter",
        required=False,
        description="What caliber of player to compare your stats to.",
        default="All",
        choices=["All"] + rank.RANKS[:-1]
    ),
):
    connected = False
    if not input_name:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message(
                "Connect your minecraft account to your discord with </connect:1149442234513637448> or specify a minecraft username.",
            )
            update_records(interaction, "analysis", "Unknown", False)
            return
        connected = True

    async def fail_get(msg):
        await interaction.response.send_message(msg)
        update_records(interaction, "analysis", input_name, False)

    print(f"---\nAnalysing {input_name}'s games")

    try:
        response = api.User(name=input_name, season=season).get()

    except api.APINotFoundError as e:
        print(e)
        not_found = f"Player not found (`{input_name}`)."
        if connected:
            await fail_get(f"{not_found} Connect to your new Minecraft username with </connect:1149442234513637448>.")
            return
        await fail_get(not_found)
        return

    except api.APIRateLimitError as e:
        print(e)
        await fail_get(API_COOLDOWN_MSG)
        return

    await interaction.response.defer()

    input_name = response["nickname"]

    target_games = int(selection[5:])
    num_comps, detailed_matches = await games.get_detailed_matches(
        response, season, 5, target_games
    )

    if detailed_matches == -1:
        print("Player does not have enough completions.")
        await interaction.followup.send(
            f"{input_name} needs a minimum of 5 completions from their last {target_games} games of season {season} to analyse. (Has {num_comps})",
        )
        update_records(interaction, "analysis", input_name, False)
        return

    rank_filter = rank.str_to_rank(rank_filter)

    try:
        anal = analysing.main(response, num_comps, detailed_matches, season, rank_filter)
    except LookupError:
        print("Not enough players in rank to compare to.")
        await interaction.followup.send(
            f"There are not enough players with matches played in {rank_filter} rank to compare to."
        )
        update_records(interaction, "analysis", input_name, False)
        return
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(f"{GENERIC_ERROR_MSG}\n```{traceback.format_exc()}```")
        update_records(interaction, "analysis", input_name, False)
        return

    head, comments, split_polygon, ow_polygon, bastion_polygon = anal

    embed_general = Embed(
        title=comments["general"]["title"],
        description=comments["general"]["description"],
        colour=nextcord.Colour.yellow(),
    )

    embed_types = ["splits", "bastion", "ow"]

    embed_split, embed_bastion, embed_ow = [
        Embed(
            title=comments[type]["title"],
            description=comments[type]["description"],
            colour=nextcord.Colour.yellow(),
        ) for type in embed_types
    ]

    embed_general.set_thumbnail(url=head)
    embed_general.set_author(
        name=interaction.user.name, icon_url=interaction.user.display_avatar.url
    )

    split_file = image_to_file(split_polygon, f"split_{input_name}.png", close=False)
    embed_split.set_image(url=f"attachment://split_{input_name}.png")

    gen_comms = comments["general"]
    for key in gen_comms:
        if key == "title" or key == "description":
            continue
        elif len(gen_comms[key]) == 1:
            value = ""
        elif key != "ffl":
            value = f"➢ {gen_comms[key][1]}\n➢ {gen_comms[key][2]}"
        else:
            value = gen_comms[key][1]

        embed_general.add_field(
            name=gen_comms[key][0],
            value=value,
            inline=True,
        )

        if key == "avg":
            embed_general.add_field(name="", value="", inline=False)

    split_comms = comments["splits"]
    for key in split_comms:
        if key == "title" or key == "description":
            continue
        elif key == "player_deaths" or key == "rank_deaths":
            embed_split.add_field(
                name=split_comms[key]["name"],
                value="\n".join(split_comms[key]["value"]),
                inline=split_comms[key]["inline"],
            )
        else:
            embed_split.add_field(
                name=split_comms[key]["name"],
                value=split_comms[key]["value"],
                inline=split_comms[key]["inline"],
            )
        if key == "worst":
            embed_split.add_field(
                name="",
                value="",
                inline=False,
            )

    bastion_comms = comments["bastion"]
    for key in bastion_comms:
        if key == "title" or key == "description":
            continue
        elif key == "player_deaths" or key == "rank_deaths":
            embed_bastion.add_field(
                name=bastion_comms[key]["name"],
                value="\n".join(bastion_comms[key]["value"]),
                inline=bastion_comms[key]["inline"],
            )
        else:
            embed_bastion.add_field(
                name=bastion_comms[key]["name"],
                value=bastion_comms[key]["value"],
                inline=bastion_comms[key]["inline"],
            )
        if key == "worst":
            embed_bastion.add_field(
                name="",
                value="",
                inline=False,
            )

    ow_comms = comments["ow"]
    for key in ow_comms:
        if key == "title" or key == "description":
            continue
        embed_ow.add_field(
            name=ow_comms[key]["name"],
            value=ow_comms[key]["value"],
            inline=ow_comms[key]["inline"],
        )

    embeds = [embed_general, embed_split, embed_bastion, embed_ow]
    for embed in embeds[1:]:
        embed.set_footer(
            text=constants.FOOTER_TEXT,
            icon_url=constants.FOOTER_ICON,
        )

    images = [split_polygon, bastion_polygon, ow_polygon]
    view = Topics(interaction, embeds, images)

    await interaction.followup.send(
        file=split_file,
        embeds=[embed_general, embed_split],
        view=view,
    )
    update_records(interaction, "analysis", input_name, True)


@card.on_autocomplete("input_name")
@plot.on_autocomplete("input_name")
@analysis.on_autocomplete("input_name")
async def name_autocomplete(interaction: Interaction, current: str):
    if not current:
        await interaction.response.send_autocomplete(player_list[:25])
        return
    near = [player for player in player_list if current.lower() in player.lower()][:25]
    await interaction.response.send_autocomplete(near)


@bot.slash_command(
    name="race",
    description="Returns a leaderboard for the current weekly race, or the race specified.",
)
async def race(
    interaction: Interaction,
    race_no: str = SlashOption(
        "race_no",
        required=False,
        description="The xth weekly race to get. Should be an integer.",
        default="",
    ),
):
    input_name = get_name(interaction)
    if race_no and race_no[0] == "#":
        race_no = race_no[1:]

    print(f"---\nFinding details about weekly race #{race_no}")
    try:
        response = api.WeeklyRace(id=race_no).get()

    except api.APINotFoundError as e:
        print(e)
        latest_race_id = api.WeeklyRace().get()["id"]
        await interaction.response.send_message(
            f"Weekly race not found (`#{race_no}`)."
            f"The latest race was weekly race `#{latest_race_id}`."
        )
        update_records(interaction, "race", race_no, False)
        return

    except api.APIRateLimitError as e:
        print(e)
        await interaction.response.send_message(API_COOLDOWN_MSG)
        update_records(interaction, "race", race_no, False)
        return

    await interaction.response.defer()

    try:
        race_embed = racing.main(response, input_name)
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(f"{GENERIC_ERROR_MSG}\n```{traceback.format_exc()}```")
        update_records(interaction, "race", race_no, False)
        return

    await interaction.followup.send(embed=race_embed)
    update_records(interaction, "race", race_no, True)


@bot.slash_command(
    name="leaderboard",
    description="Returns the leaderboard for the specified metric.",
)
async def leaderboard(interaction: Interaction):
    await leaderboard_elo(
        interaction=interaction,
        season=str(constants.SEASON),
        country="",
    )


@leaderboard.subcommand(
    name="elo",
    description="Returns the Elo leaderboard for a given season and country.",
)
async def leaderboard_elo(
    interaction: Interaction,
    season: str = SlashOption(
        "season",
        required=False,
        description="The season to display the leaderboard for.",
        default=str(constants.SEASON),
        choices=ALL_SEASONS,
    ),
    country: str = SlashOption(
        "country",
        required=False,
        description="The country to filter the leaderboard by.",
        default="",
        autocomplete=True
    ),
):
    lb_type = "elo"
    input_name = get_name(interaction)
    await interaction.response.defer()
    country_code = leading.COUNTRY_MAPPING.get(country)

    print(f"---\nFetching Elo Leaderboard for season {season} in {country} / {country_code}")
    try:
        response = api.EloLeaderboard(season=season, country=country_code).get()
    except api.APINotFoundError as e:
        print(e)
        await interaction.response.send_message(
            f"Error with finding leaderboard for season {season} in {country}"
        )
        update_records(interaction, "leaderboard", lb_type, False)
        return
    except api.APIRateLimitError as e:
        print(e)
        await interaction.response.send_message(API_COOLDOWN_MSG)
        update_records(interaction, "leaderboard", lb_type, False)
        return

    leaderboard_size = math.ceil(len(response["users"]) / 20)
    leaderboard_embeds = []

    try:
        for page in range(0, leaderboard_size):
            leaderboard_embeds.append(leading.main(response, input_name, lb_type, country, season, page))
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(f"{GENERIC_ERROR_MSG}\n```{traceback.format_exc()}```")
        update_records(interaction, "leaderboard", lb_type, False)
        return

    view = LBPage(interaction, leaderboard_embeds)

    await interaction.followup.send(embed=leaderboard_embeds[0], view=view)
    update_records(interaction, "leaderboard", lb_type, True)


@leaderboard.subcommand(
    name="phase",
    description="Returns the Phase Points leaderboard for a given season and country.",
)
async def leaderboard_phasepoints(
    interaction: Interaction,
    season: str = SlashOption(
        "season",
        required=True,
        description="The season to display the leaderboard for.",
        choices=ALL_SEASONS,
    ),
    country: str = SlashOption(
        "country",
        required=False,
        description="The country to filter the leaderboard by.",
        default="",
        autocomplete=True
    ),
):
    lb_type = "phase"
    input_name = get_name(interaction)
    await interaction.response.defer()
    country_code = leading.COUNTRY_MAPPING.get(country)

    print(f"---\nFetching Phase Points Leaderboard for season {season} in {country} / {country_code}")
    try:
        response = api.PhaseLeaderboard(season=season, country=country_code).get()
    except api.APINotFoundError as e:
        print(e)
        await interaction.response.send_message(
            f"Error with finding leaderboard for season {season} in {country}"
        )
        update_records(interaction, "leaderboard", lb_type, False)
        return
    except api.APIRateLimitError as e:
        print(e)
        await interaction.response.send_message(API_COOLDOWN_MSG)
        update_records(interaction, "leaderboard", lb_type, False)
        return

    leaderboard_size = math.ceil(len(response["users"]) / 20)
    leaderboard_embeds = []

    try:
        for page in range(0, leaderboard_size):
            leaderboard_embeds.append(leading.main(response, input_name, lb_type, country, season, page))
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(f"{GENERIC_ERROR_MSG}\n```{traceback.format_exc()}```")
        update_records(interaction, "leaderboard", lb_type, False)
        return

    view = LBPage(interaction, leaderboard_embeds)

    await interaction.followup.send(embed=leaderboard_embeds[0], view=view)
    update_records(interaction, "leaderboard", lb_type, True)


@leaderboard_elo.on_autocomplete("country")
@leaderboard_phasepoints.on_autocomplete("country")
async def leaderboard_country_autocomplete(interaction: Interaction, current: str):
    if not current:
        await interaction.response.send_autocomplete(ALL_COUNTRIES[:25])
        return
    near = [country for country in ALL_COUNTRIES if current.lower() in country.lower()][:25]
    await interaction.response.send_autocomplete(near)


@leaderboard.subcommand(
    name="completion",
    description="Returns the Completion Time leaderboard for a given season.",
)
async def leaderboard_completiontime(
    interaction: Interaction,
    season: str = SlashOption(
        "season",
        required=True,
        description="The season to display the leaderboard for.",
        choices=ALL_SEASONS + ["Lifetime"],
    ),
):
    lb_type = "completion"
    input_name = get_name(interaction)
    await interaction.response.defer()

    print(f"---\nFetching Completion Time Leaderboard for season {season}")
    if season == "Lifetime":
        season = None
    try:
        response = api.RecordLeaderboard(season=season).get()
    except api.APINotFoundError as e:
        print(e)
        await interaction.response.send_message(
            f"Error with finding leaderboard for season {season}"
        )
        update_records(interaction, "leaderboard", lb_type, False)
        return
    except api.APIRateLimitError as e:
        print(e)
        await interaction.response.send_message(API_COOLDOWN_MSG)
        update_records(interaction, "leaderboard", lb_type, False)
        return

    leaderboard_size = math.ceil(len(response) / 20)
    leaderboard_embeds = []

    try:
        for page in range(0, leaderboard_size):
            leaderboard_embeds.append(leading.main(response, input_name, lb_type, "", season, page))
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(f"{GENERIC_ERROR_MSG}\n```{traceback.format_exc()}```")
        update_records(interaction, "leaderboard", lb_type, False)
        return

    view = LBPage(interaction, leaderboard_embeds)

    await interaction.followup.send(embed=leaderboard_embeds[0], view=view)
    update_records(interaction, "leaderboard", lb_type, True)


@bot.slash_command(
    name="live",
    description="Checks which Ranked streamers are live.",
)
async def live(interaction: Interaction):
    print(f"---\nChecking who's live")
    await interaction.response.defer()

    try:
        response = api.Live().get()
    except api.APIRateLimitError as e:
        print(e)
        await interaction.response.send_message(API_COOLDOWN_MSG)
        update_records(interaction, "live", type, False)
        return

    embed = Embed(
        title="MCSR Ranked Live Players",
        description=f"There are {response['players']} players online.",
        colour=nextcord.Colour.brand_red()
    )
    for match in sorted(
        response["liveMatches"],
        key=lambda x: max(
            player["eloRate"] if player["eloRate"] is not None else 0
            for player in x["players"]
        ),
        reverse=True
    ):
        name = ""
        value = ""

        player_tags = []
        player_links = []
        for player in sorted(
            match["players"],
            key=lambda x: x["eloRate"] if x["eloRate"] is not None else 0,
            reverse=True
        ):
            player_rank = rank.get_rank(player["eloRate"])
            rank_emote = rank.get_emote(player_rank)
            player_tags.append(
                f"{rank_emote} "
                f"#{player['eloRank']} "
                f"{player['nickname']}"
            )
            player_links.append(
                f"[{player['nickname']}]"
                f"({match['data'][player['uuid']]['liveUrl']})"
            )
        name = " vs ".join(player_tags)
        value = ", ".join(player_links)

        timestamp = int(time() - match["currentTime"] / 1000)
        value += f"\nMatch began <t:{timestamp}:R>."

        embed.add_field(name=name, value=value, inline=False)

    embed.add_field(
        name="Want to show up when you're live?",
        value="Link your twitch to MCSR Ranked in-game.\nTurn the 'Public Stream: Twitch' option on in Ranked settings.",
        inline=False,
    )
    embed.set_footer(
        text=constants.FOOTER_TEXT,
        icon_url=constants.FOOTER_ICON,
    )

    await interaction.followup.send(embed=embed)
    update_records(interaction, "live", type, True)


@bot.slash_command(
    name="customise",
    description="Allows you to personalise your card. Only applies to connected users.",
)
async def customise(
    interaction: Interaction,
    background: str = SlashOption(
        "background",
        required=True,
        description="Your background of choice for your card.",
        default="Classic",
        choices=[
            "Classic",
            "Overworld",
            "Bastion",
            "Fortress",
            "Portal",
            "Stronghold",
            "The End",
        ],
    ),
):

    input_name = get_name(interaction)
    if not input_name:
        await interaction.response.send_message(
            "Please connect your minecraft account to your discord with </connect:1149442234513637448> to customise your card.",
        )
        update_records(interaction, "background", background, False)
        return

    uid = str(interaction.user.id)
    bg_mapping = {
        "Classic": "grass.jpg",
        "Overworld": "beach.jpg",
        "Bastion": "bastion.jpg",
        "Fortress": "fort.jpg",
        "Portal": "portal.jpg",
        "Stronghold": "stronghold.jpg",
        "The End": "end.jpg",
    }

    file = path.join("src", "database", "users.json")
    with open(file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if uid == user["discord"]:
            user["background"] = bg_mapping[background]
            user_exists = True
            break

    if not user_exists:
        await interaction.response.send_message(
            "An error has occurred. <@298936021557706754> fix it pls"
        )
        update_records(interaction, "background", background, False)
        return

    with open(file, "w") as f:
        users_json = json.dumps(users, indent=4)
        f.write(users_json)

    await interaction.response.send_message(
        f"Updated your card background to {background}!"
    )
    update_records(interaction, "background", background, True)
    return


@bot.slash_command(
    name="connect",
    description="Connects your minecraft account with your discord account.",
)
async def connect(interaction: Interaction, input_name: str):

    uid = str(interaction.user.id)
    user_exists = False
    user_id = 0

    file = path.join("src", "database", "users.json")
    with open(file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if uid == user["discord"]:
            user_exists = True
            user_id = users["users"].index(user)
        elif input_name.lower() == user["minecraft"].lower():
            await interaction.response.send_message(
                f"`{input_name}` is already connected to {bot.get_user(int(user['discord']))}."
            )
            update_records(interaction, "connect", input_name, False)
            return

    if not user_exists:
        new_user = {
            "minecraft": input_name,
            "discord": uid,
            "background": "grass.jpg",
            "cooldown": 0,
            "last_link": "",
        }
        users["users"].append(new_user)
    else:
        users["users"][user_id]["minecraft"] = input_name

    with open(file, "w") as f:
        users_json = json.dumps(users, indent=4)
        f.write(users_json)

    await interaction.response.send_message(
        f"`{input_name}` has been connected to your discord!"
    )
    update_records(interaction, "connect", input_name, not user_exists)


@bot.slash_command(
    name="disconnect",
    description="Disconnects your minecraft account from your discord account.",
)
async def disconnect(interaction: Interaction):

    uid = str(interaction.user.id)

    file = path.join("src", "database", "users.json")
    with open(file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if uid == user["discord"]:
            users["users"].remove(user)

            with open(file, "w") as f:
                print(users)
                users_json = json.dumps(users, indent=4)
                f.write(users_json)
            await interaction.response.send_message(
                f"`{user['minecraft']}` has been disconnected from your discord."
            )
            update_records(interaction, "disconnect", user["minecraft"], True)
            return

    await interaction.response.send_message(
        f"You are not connected. Please connect your minecraft account with </connect:1149442234513637448> to your discord."
    )
    update_records(interaction, "disconnect", "Unknown", False)


@bot.slash_command(name="help", description="Don't know where to start?")
async def help(
    interaction: Interaction,
):

    embed = Embed(
        title="Ranked Stats - Help and Commands",
        description="This is the MCSR Ranked Stats bot, made by @Nadoms. Any questions, just dm me :)\nThese are the current available commands:",
        colour=nextcord.Colour.yellow(),
    )

    embed.set_thumbnail(
        url=r"https://mcsrranked.com/_next/image?url=%2Ftest1.png&w=640&q=75"
    )
    embed.add_field(
        name="/card",
        value="`Options: Minecraft username`\n`Defaults: Connected user`\nGenerates the ***statistics card*** for the player that you input.",
        inline=False,
    )
    embed.add_field(
        name="/plot",
        value="`Options: Minecraft username, type of data, season`\n`Defaults: Connected user, elo, current season`\n***Plots a graph*** for the type of data (Elo / Completion time) across the timeframe and for the player you specify.",
        inline=False,
    )
    embed.add_field(
        name="/match",
        value="`Options: Match ID`\n`Defaults: Last ranked match played`\n***Draws a chart*** visualising two player's splits in a game.",
        inline=False,
    )
    embed.add_field(
        name="/analysis",
        value="`Options: Minecraft username, season, number of games, rank filter`\n`Defaults: Connected user, current season, up to last 300 games, any rank`\n***Analyses your games*** to give feedback about splits, bastions and overworlds.",
        inline=False,
    )
    embed.add_field(
        name="/race",
        value="`Options: Weekly race number`\n`Defaults: Current race`\n***Returns the leaderboard*** for the weekly race specified.",
        inline=False,
    )
    embed.add_field(
        name="/leaderboard",
        value="`Options: Leaderboard type, season, country`\n`Defaults: Elo, current season, any country`\n***Returns the leaderboard*** for Elo / Fastest Completion / Phase Points, filtered by the season and country if specified.",
        inline=False,
    )
    embed.add_field(
        name="/live",
        value="***Lists current live players*** in MCSR Ranked games.",
        inline=False,
    )
    embed.add_field(
        name="/customise",
        value="`Options: Card background`\n`Defaults: Classic`\n***Customises your card*** how you specify, currently with the background.",
        inline=False,
    )
    embed.add_field(
        name="/connect",
        value="`Options: Minecraft username`\n***Connects your discord account*** to a Minecraft username so that you don't have to write it when doing the other commands.",
        inline=False,
    )
    embed.add_field(
        name="/disconnect",
        value="***Removes the connected Minecraft account*** from your discord, useful if you changed name or switched account.",
        inline=False,
    )

    await interaction.send(embed=embed)
    update_records(interaction, "help", "None", True)


def get_user_info(response, input_name):
    file = path.join("src", "database", "users.json")
    with open(file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if input_name.lower() == user["minecraft"].lower():
            return user["discord"], user["background"]

    if "discord" in response["connections"]:
        uid = response["connections"]["discord"]["id"]
        return uid, "grass.jpg"

    return "343108228890099713", "grass.jpg"


def get_name(interaction_ctx):
    try:
        uid = str(interaction_ctx.user.id)
    except:
        uid = str(interaction_ctx.message.author.id)

    file = path.join("src", "database", "users.json")
    with open(file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if uid == user["discord"]:
            return user["minecraft"]

    return ""


def update_records(interaction, command, subject, completed):
    if TESTING_MODE:
        return
    calls_file = path.join("src", "database", "calls_24.csv")
    stats_file = path.join("src", "database", "stats.json")
    caller_id = interaction.user.id
    caller_name = interaction.user.name
    if isinstance(interaction.channel, nextcord.PartialMessageable) or not interaction.guild:
        channel_name = None
        guild_name = None
    else:
        channel_name = interaction.channel.name
        guild_name = interaction.guild.name

    with open(calls_file, "a") as f:
        row = f"\n{command},{subject},{caller_id},{caller_name},{channel_name},{guild_name},{int(time())},,{completed}"
        f.write(row)

    with open(stats_file, "r") as f:
        stats = json.load(f)

    stats["stats"]["totalCommands"] += 1

    if command == "card":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["cards"]["success"] += completed
        stats["stats"]["cards"]["fail"] += 1 - completed

    elif command == "plot":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["plots"]["success"] += completed
        stats["stats"]["plots"]["fail"] += 1 - completed

    elif command == "match":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["matches"]["success"] += completed
        stats["stats"]["matches"]["fail"] += 1 - completed

    elif command == "analysis":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["analyses"]["success"] += completed
        stats["stats"]["analyses"]["fail"] += 1 - completed

    elif command == "race":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["races"]["success"] += completed
        stats["stats"]["races"]["fail"] += 1 - completed

    elif command == "leaderboard":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["leaderboards"]["success"] += completed
        stats["stats"]["leaderboards"]["fail"] += 1 - completed

    elif command == "live":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["lives"]["success"] += completed
        stats["stats"]["lives"]["fail"] += 1 - completed

    elif command == "connect":
        stats["stats"]["connectedUsers"] += 1
        stats["stats"]["connects"]["success"] += completed
        stats["stats"]["connects"]["fail"] += 1 - completed

    elif command == "disconnect":
        stats["stats"]["connectedUsers"] -= 1
        stats["stats"]["disconnects"]["success"] += completed
        stats["stats"]["disconnects"]["fail"] += 1 - completed

    elif command == "help":
        stats["stats"]["helps"] += 1

    elif command == "background":
        stats["stats"]["backgrounds"] += 1

    with open(stats_file, "w") as f:
        stats_json = json.dumps(stats, indent=4)
        f.write(stats_json)


def image_to_file(image, filename, close=True):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    file = File(buffer, filename=filename)
    if close:
        image.close()
    return file


async def fetch_loop():
    latest_load = START_ID
    repeat = 900
    while True:
        not_latest_load = latest_load
        latest_load = await load_matches.spam_redlime(latest_load, 1000)
        await asyncio.sleep(repeat)
        if not_latest_load == latest_load:
            print("No new matches found.")
            repeat = 7200
        else:
            repeat = 900


async def suggestions_loop():
    await asyncio.sleep(60)
    while True:
        global player_list
        player_list = construct_players.construct_player_list()
        await asyncio.sleep(86400)


async def analysis_loop():
    await asyncio.sleep(120)
    while True:
        await analyse_db.analyse(constants.SEASON)
        await asyncio.sleep(86400)


if not TESTING_MODE:
    bot.loop.create_task(fetch_loop())
    bot.loop.create_task(suggestions_loop())
    bot.loop.create_task(analysis_loop())
load_dotenv()
bot.run(getenv(token))
