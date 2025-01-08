import difflib
import os
import nextcord
import json
from nextcord import File, Interaction, ApplicationError, SlashOption, Embed, Colour
from nextcord.ext import commands
from os import getenv, path
from dotenv import load_dotenv
from time import time
from datetime import datetime, timezone
import traceback

from commands import (
    card as carding,
    graph as graphing,
    match as matching,
    analysis as analysing,
    race as racing,
)
from gen_functions import games, api

TESTING_MODE = True
CURRENT_SEASON = games.get_season()
ALL_SEASONS = [str(season) for season in range(1, CURRENT_SEASON + 1)]
API_COOLDOWN_MSG = "Too many commands have been issued! The Ranked API is cooling down... (~10 mins)"
token = "TEST_TOKEN" if TESTING_MODE else "DISCORD_TOKEN"
default_guild_ids = [735859906434957392] if TESTING_MODE else None

intents = intents = nextcord.Intents.all()
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

    def image_to_file(self, embed, image):
        image.save(f"{self.value}.png")
        file = File(f"{self.value}.png", filename=f"{self.value}.png")
        embed.set_image(url=f"attachment://{self.value}.png")
        os.remove(f"{self.value}.png")
        return file

    @nextcord.ui.button(label="Splits", style=nextcord.ButtonStyle.red)
    async def show_splits(
        self,
        button: nextcord.ui.Button,
        interaction: Interaction,
    ):
        print(f"Flipping to splits for {interaction.user.name}")
        self.value = "splits"
        file = self.image_to_file(self.topic_embeds[0], self.images[0])
        await self.interaction.edit_original_message(
            embeds=[self.general_embed, self.topic_embeds[0]],
            file=file,
        )

    @nextcord.ui.button(label="Bastions", style=nextcord.ButtonStyle.blurple)
    async def show_bastions(
        self,
        button: nextcord.ui.Button,
        interaction: Interaction,
    ):
        print(f"Flipping to bastions for {interaction.user.name}")
        self.value = "bastions"
        file = self.image_to_file(self.topic_embeds[1], self.images[1])
        await self.interaction.edit_original_message(
            embeds=[self.general_embed, self.topic_embeds[1]],
            file=file,
        )

    @nextcord.ui.button(label="Overworlds", style=nextcord.ButtonStyle.green)
    async def show_overworlds(
        self,
        button: nextcord.ui.Button,
        interaction: Interaction,
    ):
        print(f"Flipping to overworlds for {interaction.user.name}")
        self.value = "ows"
        file = self.image_to_file(self.topic_embeds[2], self.images[2])
        await self.interaction.edit_original_message(
            embeds=[self.general_embed, self.topic_embeds[2]],
            file=file,
        )


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
        close_names = get_close(input_name)
        if close_names:
            await fail_get(f"{not_found} Similar usernames include:\n{', '.join(close_names)}")
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
        await interaction.followup.send(
            "An error has occurred. <@298936021557706754> fix it pls:\n"
            f"```{traceback.format_exc()}```"
        )
        update_records(interaction, "card", input_name, False)
        return

    img.save(f"card_{input_name}.png")
    img.close()
    with open(f"card_{input_name}.png", "rb") as f:
        img = File(f)
    await interaction.followup.send(file=img)
    update_records(interaction, "card", input_name, True)
    os.remove(f"card_{input_name}.png")


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
        default=str(CURRENT_SEASON),
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
        close_names = get_close(input_name)
        if close_names:
            await fail_get(f"{not_found} Similar usernames include:\n{', '.join(close_names)}")
            return
        await fail_get(not_found)
        return

    except api.APIRateLimitError as e:
        print(e)
        await fail_get(API_COOLDOWN_MSG)
        return

    await interaction.response.defer()

    input_name = response["nickname"]
    matches = await games.get_matches(response["nickname"], season, True)

    try:
        img = graphing.main(input_name, response, type, season, matches)
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(
            "An error has occurred. <@298936021557706754> fix it pls:\n"
            f"```{traceback.format_exc()}```"
        )
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

    img.save(f"graph_{input_name}.png")
    img.close()
    with open(f"graph_{input_name}.png", "rb") as f:
        img = File(f)
    await interaction.followup.send(file=img)
    update_records(interaction, "plot", input_name, True)
    os.remove(f"graph_{input_name}.png")


@bot.slash_command(
    name="match",
    description="Produces a chart on your most recent match, or the match specified.",
)
async def match(
    interaction: Interaction,
    match_id: str = SlashOption(
        "match_id",
        required=False,
        description="The match ID to draw a chart of.",
        default=None,
    ),
):
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
            match_response = api.UserMatches(
                name=input_name, count=1, type=2, excludedecay=True
            ).get()
        except api.APIRateLimitError as e:
            print(e)
            await interaction.response.send_message(API_COOLDOWN_MSG)
            update_records(interaction, "match", "Unknown", False)
            return

        if match_response == []:
            await interaction.response.send_message(
                f"Player has no matches from this season. ({input_name})"
            )
            update_records(interaction, "match", "Unknown", False)
            return

        match_id = match_response[0]["id"]

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
        await interaction.followup.send(
            "An error has occurred. <@298936021557706754> fix it pls:\n"
            f"```{traceback.format_exc()}```"
        )
        update_records(interaction, "match", match_id, False)
        return

    img.save(f"chart_{match_id}.png")
    img.close()
    with open(f"chart_{match_id}.png", "rb") as f:
        img = File(f)
    await interaction.followup.send(file=img)
    update_records(interaction, "match", match_id, True)
    os.remove(f"chart_{match_id}.png")


@bot.slash_command(
    name="analysis",
    description="Analyses 100+ games from any season to visualise how a player performs throughout their runs.",
)
async def analysis(
    interaction: Interaction,
    input_name: str = SlashOption(
        "name", required=False, description="The player to analyse.", default=""
    ),
    season: str = SlashOption(
        "season",
        required=False,
        description="The season to gather data from.",
        default=str(CURRENT_SEASON),
        choices=ALL_SEASONS,
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
        close_names = get_close(input_name)
        if close_names:
            await fail_get(f"{not_found} Similar usernames include:\n{', '.join(close_names)}")
            return
        await fail_get(not_found)
        return

    except api.APIRateLimitError as e:
        print(e)
        await fail_get(API_COOLDOWN_MSG)
        return

    await interaction.response.defer()

    input_name = response["nickname"]
    cooldown = 60 * 30  # 30 min cooldown
    user_cooldown, last_link = get_cooldown(input_name)

    cd_extra = ""
    if last_link:
        last_guild = int(last_link.split("/")[-3])
        if last_guild == interaction.guild.id:
            cd_extra = f"\nTheir last analysis is {last_link}"

    delta = int(time()) - user_cooldown
    if delta < cooldown and not input_name == "Nadoms":
        next_available = f"<t:{user_cooldown + cooldown}:R>"
        print("Command on cooldown.")
        await interaction.followup.send(
            f"This command is on cooldown for `{input_name}`. (You can use it {next_available}){cd_extra}",
        )
        update_records(interaction, "analysis", input_name, False)
        return

    target_games = 200 if TESTING_MODE else 200
    num_comps, detailed_matches = await games.get_detailed_matches(
        response, season, 5, target_games
    )

    if detailed_matches == -1:
        print("Player does not have enough completions.")
        await interaction.followup.send(
            f"{input_name} needs a minimum of 5 completions from season {season} to analyse. (Has {num_comps})",
        )
        update_records(interaction, "analysis", input_name, False)
        return

    try:
        anal = analysing.main(response, num_comps, detailed_matches, season)
    except Exception:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send(
            "An error has occurred. <@298936021557706754> fix it pls:\n"
            f"```{traceback.format_exc()}```"
        )
        update_records(interaction, "analysis", input_name, False)
        return

    head, comments, split_polygon, ow_polygon, bastion_polygon = anal

    embed_general = nextcord.Embed(
        title=comments["general"]["title"],
        description=comments["general"]["description"],
        colour=nextcord.Colour.yellow(),
    )
    embed_split = nextcord.Embed(
        title=comments["splits"]["title"],
        description=comments["splits"]["description"],
        colour=nextcord.Colour.yellow(),
        timestamp=datetime.now(timezone.utc),
    )
    embed_bastion = nextcord.Embed(
        title=comments["bastion"]["title"],
        description=comments["bastion"]["description"],
        colour=nextcord.Colour.yellow(),
        timestamp=datetime.now(timezone.utc),
    )
    embed_ow = nextcord.Embed(
        title=comments["ow"]["title"],
        description=comments["ow"]["description"],
        colour=nextcord.Colour.yellow(),
        timestamp=datetime.now(timezone.utc),
    )

    embed_general.set_thumbnail(url=head)
    embed_general.set_author(
        name=interaction.user.name, icon_url=interaction.user.display_avatar.url
    )

    split_polygon.save(f"split_{input_name}.png")
    split_file = File(f"split_{input_name}.png", filename=f"split_{input_name}.png")
    embed_split.set_image(url=f"attachment://split_{input_name}.png")
    embed_split.set_footer(
        text="Bot made by @Nadoms // Feedback appreciated :3",
        icon_url="https://cdn.discordapp.com/avatars/298936021557706754/a_60fb14a1dbfb0d33f3b02cc33579dacf?size=256",
    )

    embed_bastion.set_footer(
        text="Bot made by @Nadoms // Feedback appreciated :3",
        icon_url="https://cdn.discordapp.com/avatars/298936021557706754/a_60fb14a1dbfb0d33f3b02cc33579dacf?size=256",
    )

    embed_ow.set_footer(
        text="Bot made by @Nadoms // Feedback appreciated :3",
        icon_url="https://cdn.discordapp.com/avatars/298936021557706754/a_60fb14a1dbfb0d33f3b02cc33579dacf?size=256",
    )

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

    jump_url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.id}"
    if not TESTING_MODE or interaction.guild.id != 1056779246728658984:
        set_cooldown(jump_url, input_name)
    embeds = [embed_general, embed_split, embed_bastion, embed_ow]
    images = [split_polygon, bastion_polygon, ow_polygon]
    view = Topics(interaction, embeds, images)

    await interaction.followup.send(
        file=split_file,
        embeds=[embed_general, embed_split],
        view=view,
    )
    update_records(interaction, "analysis", input_name, True)
    os.remove(f"split_{input_name}.png")


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
        await interaction.followup.send(
            "An error has occurred. <@298936021557706754> fix it pls:\n"
            f"```{traceback.format_exc()}```"
        )
        update_records(interaction, "race", race_no, False)
        return

    await interaction.followup.send(embed=race_embed)
    update_records(interaction, "race", race_no, True)


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

    embed = nextcord.Embed(
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
        value="`Options: Minecraft username, type of data [Elo / Completion time], season [Lifetime/1/2/3/4/5]`\n`Defaults: Connected user, Elo, S4`\n***Plots a graph*** for the type of data (Elo / Completion time) across the timeframe (Season 1/2/3/4 / Lifetime) and for the player you specify.",
        inline=False,
    )
    embed.add_field(
        name="/match",
        value="`Options: Match ID`\n`Defaults: Last ranked match played`\n***Draws a chart*** visualising two player's splits in a game.",
        inline=False,
    )
    embed.add_field(
        name="/analysis",
        value="`Options: Minecraft username`\n`Defaults: Connected user`\n***Analyses your games*** to give feedback about splits and overworlds.",
        inline=False,
    )
    embed.add_field(
        name="/race",
        value="`Options: Weekly race number`\n`Defaults: Current race`\n***Returns the leaderboard*** for the weekly race specified.",
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


def get_cooldown(input_name):
    file = path.join("src", "database", "users.json")
    with open(file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if input_name == user["minecraft"]:
            return user["cooldown"], user["last_link"]

    return False, False


def set_cooldown(jump_url, input_name):
    file = path.join("src", "database", "users.json")
    with open(file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if input_name == user["minecraft"]:
            user["cooldown"] = int(time())
            user["last_link"] = jump_url
            break

    with open(file, "w") as f:
        users_json = json.dumps(users, indent=4)
        f.write(users_json)


def get_close(input_name):
    file = path.join("src", "database", "players.txt")
    with open(file, "r") as f:
        players = f.readlines()
    close_names = [
        f"`{name.strip()}`"
        for name in difflib.get_close_matches(input_name, players)[:10]
    ]
    return close_names


def update_records(interaction, command, subject, completed):
    if TESTING_MODE:
        return
    calls_file = path.join("src", "database", "calls_24.csv")
    stats_file = path.join("src", "database", "stats.json")
    caller_id = interaction.user.id
    caller_name = interaction.user.name
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


load_dotenv()
bot.run(getenv(token))
