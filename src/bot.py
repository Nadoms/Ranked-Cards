import difflib
import nextcord
import json
from nextcord import File, Interaction, ApplicationError, SlashOption, Embed, Colour
from nextcord.ext import commands
from os import getenv, path
from dotenv import load_dotenv
from time import time
from datetime import datetime, timezone
import traceback

import requests
from commands import card as carding, graph as graphing, match as matching, analysis as analysing, race as racing
from gen_functions import games

intents = intents=nextcord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="=", intents=intents, default_guild_ids=[735859906434957392, 1113914901325434880, 1056779246728658984])
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}

@bot.event
async def on_ready():
    print("Bot is running")

# SLASH COMMANDS
@bot.slash_command(name="ping", description="Pong!")
async def ping(interaction: Interaction):
    await interaction.response.send_message("Pong!")


@bot.slash_command(name="card", description="Generates a card for the player you specify.")
async def card(interaction: Interaction, input_name: str = SlashOption(
    "name",
    required = False,
    description="The player to generate a card for.",
    default = ""
    ), hidden: str = SlashOption(
    "hidden",
    required = False,
    description="Hides my response.",
    default="",
    choices=["True"]
    )):
    
    if hidden:
        hidden = True
    else:
        hidden = False

    connected = False
        
    if not input_name:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message("Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a minecraft username.", ephemeral=hidden)
            update_records("card", interaction.user.id, "Unknown", hidden, False)
            return
        connected = True
    
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}", headers=HEADERS).json()
    
    print(f"\nGenerating card for {input_name}")
    failed = False
    if response["status"] == "error":
        if response["data"] == "Too many requests":
            await interaction.response.send_message(f"Too many commands have been issued! The Ranked API is cooling down...", ephemeral=hidden)
            print(f"\nRanked API is mad at me...")
            update_records("card", interaction.user.id, input_name, hidden, False)
            return

        print(f"Player not found (`{input_name}`).")
        if connected:
            await interaction.response.send_message(f"Player not found (`{input_name}`). Connect to your new Minecraft username with </connect:1149442234513637448>.", ephemeral=hidden)
            update_records("card", interaction.user.id, input_name, hidden, False)
            return
        
        failed = True
        extra, first = get_close(input_name)

        if not first:
            await interaction.response.send_message(f"Player not found (`{input_name}`).", ephemeral=hidden)
            update_records("card", interaction.user.id, input_name, hidden, False)
            return
        else:
            print(f"\nAutocorrected to {first}.")
            response = requests.get(f"https://mcsrranked.com/api/users/{first}", headers=HEADERS).json()

            if response["status"] == "error":
                print("Player changed username.")
                extra = " This player may have changed username."
                await interaction.response.send_message(f"Player not found (`{input_name}`). {extra}", ephemeral=hidden)
                update_records("card", interaction.user.id, input_name, hidden, False)
                return
        
    await interaction.response.defer(ephemeral=hidden)
    response = response["data"]

    old_input = input_name
    input_name = response["nickname"]
    uid, background = get_user_info(response, input_name)
    user = await bot.fetch_user(uid)
    pfp = user.avatar
    if not pfp:
        pfp = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"
    discord = str(user)
    if discord[-2:] == "#0":
        discord = discord[:-2]

    history = await games.get_user_matches(name=input_name, page=0, count=50)
    
    try:
        img = carding.main(input_name, response, discord, pfp, background, history)
    except Exception as e:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls", ephemeral=hidden)
        update_records("card", interaction.user.id, input_name, hidden, False)
        return

    img.save("card.png")
    with open("card.png", "rb") as f:
        img = File(f)
    if failed:
        await interaction.followup.send(f"Player not found (`{old_input}`). {extra}", file=img, ephemeral=hidden)
        update_records("card", interaction.user.id, input_name, hidden, True)
    else:
        await interaction.followup.send(file=img, ephemeral=hidden)
        update_records("card", interaction.user.id, input_name, hidden, True)


@bot.slash_command(name="plot", description="Illustrates a graph for the player + metric that you choose.")
async def plot(interaction: Interaction, input_name: str = SlashOption(
    "name",
    required = False,
    description="The player to draw a graph for.",
    default=""
    ), type: str = SlashOption(
    "type",
    required = False,
    description="The metric to plot.",
    default="Elo",
    choices=["Elo", "Completion time"]
    ), season: str = SlashOption(
    "season",
    required = False,
    description="The season to gather data for.",
    default="6",
    choices=["1", "2", "3", "4", "5", "6", "Lifetime"]
    ), hidden: str = SlashOption(
    "hidden",
    required = False,
    description="Hides my response.",
    default="",
    choices=["True"]
    )):
    
    if hidden:
        hidden = True
    else:
        hidden = False

    connected = False
        
    if not input_name:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message("Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a minecraft username.", ephemeral=hidden)
            update_records("plot", interaction.user.id, "Unknown", hidden, False)
            return
        connected = True
    
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}", headers=HEADERS).json()
        
    print(f"\nDrawing {type} graph for {input_name}")
    failed = False
    if response["status"] == "error":
        if response["data"] == "Too many requests":
            await interaction.response.send_message(f"Too many commands have been issued! The Ranked API is cooling down...", ephemeral=hidden)
            print(f"\nRanked API is mad at me...")
            update_records("plot", interaction.user.id, input_name, hidden, False)
            return

        print(f"Player not found (`{input_name}`).")
        if connected:
            await interaction.response.send_message(f"Player not found (`{input_name}`). Connect to your new Minecraft username with </connect:1149442234513637448>.", ephemeral=hidden)
            update_records("plot", interaction.user.id, input_name, hidden, False)
            return
        
        failed = True
        extra, first = get_close(input_name)

        if not first:
            await interaction.response.send_message(f"Player not found  (`{input_name}`).", ephemeral=hidden)
            update_records("plot", interaction.user.id, input_name, hidden, False)
            return
        else:
            print(f"\nAutocorrected to {first}.")
            response = requests.get(f"https://mcsrranked.com/api/users/{first}", headers=HEADERS).json()

            if response["status"] == "error":
                print("Player changed username.")
                extra = " This player may have changed username."
                await interaction.response.send_message(f"Player not found (`{input_name}`). {extra}", ephemeral=hidden)
                update_records("plot", interaction.user.id, input_name, hidden, False)
                return
    
    await interaction.response.defer(ephemeral=hidden)
    response = response["data"]

    old_input = input_name
    input_name = response["nickname"]

    matches = await games.get_matches(response["nickname"], season, True)
    
    try:
        img = graphing.main(input_name, response, type, season, matches)
    except Exception as e:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls", ephemeral=hidden)
        update_records("plot", interaction.user.id, input_name, hidden, False)
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
        await interaction.followup.send(f"`{input_name}` has not enough {msg1}{msg2}.", ephemeral=hidden)
        update_records("plot", interaction.user.id, input_name, hidden, False)
        return

    img.save("graph.png")
    with open("graph.png", "rb") as f:
        img = File(f)
    if failed:
        await interaction.followup.send(f"Player not found (`{old_input}`). {extra}", file=img, ephemeral=hidden)
        update_records("plot", interaction.user.id, input_name, hidden, True)
    else:
        await interaction.followup.send(file=img, ephemeral=hidden)
        update_records("plot", interaction.user.id, input_name, hidden, True)


@bot.slash_command(name="match", description="Produces a chart on your most recent match, or the match specified.")
async def match(interaction: Interaction, match_id: str = SlashOption(
    "match_id",
    required = False,
    description="The match ID to draw a chart of.",
    default=None
    ), hidden: str = SlashOption(
    "hidden",
    required = False,
    description="Hides my response.",
    default="",
    choices=["True"]
    )):
    
    if hidden:
        hidden = True
    else:
        hidden = False

    input_name = get_name(interaction)

    if not match_id:
        if not input_name:
            await interaction.response.send_message("Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a match ID.", ephemeral=hidden)
            update_records("match", interaction.user.id, "Unknown", hidden, False)
            return

        print(f"\nFinding {input_name}'s last match")
        match_id = games.get_last_match(input_name)
        if not match_id:
            await interaction.response.send_message("Player has no matches from this season.", ephemeral=hidden)
            update_records("match", interaction.user.id, "Unknown", hidden, False)
            return
        
        if match_id == -1:
            await interaction.response.send_message(f"Too many commands have been issued! The Ranked API is cooling down...", ephemeral=hidden)
            print(f"\nRanked API is mad at me...")
            update_records("match", interaction.user.id, "Unknown", hidden, False)
            return


    print(f"\nCharting match {match_id}")
    response = requests.get(f"https://mcsrranked.com/api/matches/{match_id}", headers=HEADERS).json()

    if response["status"] == "error":
        if response["data"] == "Too many requests":
            await interaction.response.send_message(f"Too many commands have been issued! The Ranked API is cooling down...", ephemeral=hidden)
            print(f"\nRanked API is mad at me...")
            update_records("match", interaction.user.id, input_name, hidden, False)
            return

        print("Match not found.")
        await interaction.response.send_message(f"Match not found. (`{match_id}`)", ephemeral=hidden)
        update_records("match", interaction.user.id, match_id, hidden, False)
        return
    
    response = response["data"]
    
    if response["type"] >= 3 or response["decayed"] == True:
        print("Match is invalid.")
        await interaction.response.send_message(f"Match must be a ranked or casual game. (`{match_id}`)", ephemeral=hidden)
        update_records("match", interaction.user.id, match_id, hidden, False)
        return
    
    await interaction.response.defer(ephemeral=hidden)
    
    try:
        img = matching.main(response)
    except Exception as e:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls", ephemeral=hidden)
        update_records("match", interaction.user.id, match_id, hidden, False)
        return

    img.save("chart.png")
    with open("chart.png", "rb") as f:
        img = File(f)
    await interaction.followup.send(file=img, ephemeral=hidden)
    update_records("match", interaction.user.id, match_id, hidden, True)


@bot.slash_command(name="analysis", description="Analyses 100+ games from any season to visualise how a player performs throughout their runs.")
async def analysis(interaction: Interaction, input_name: str = SlashOption(
    "name",
    required = False,
    description="The player to analyse.",
    default = ""
    ), season: str = SlashOption(
    "season",
    required = False,
    description="The season to gather data from.",
    default="6",
    choices=["1", "2", "3", "4", "5", "6"]
    ), hidden: str = SlashOption(
    "hidden",
    required = False,
    description="Hides my response.",
    default="",
    choices=["True"]
    )):
    
    if hidden:
        hidden = True
    else:
        hidden = False

    connected = False

    if not input_name:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message("Connect your minecraft account to your discord with </connect:1149442234513637448> or specify a minecraft username.", ephemeral=hidden)
            update_records("analysis", interaction.user.id, "Unknown", hidden, False)
            return
        connected = True

    print(f"\nAnalysing {input_name}'s games")

    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}", headers=HEADERS).json()

    failed = False
    if response["status"] == "error":
        if response["data"] == "Too many requests":
            await interaction.response.send_message(f"Too many commands have been issued! The Ranked API is cooling down...", ephemeral=hidden)
            print(f"\nRanked API is mad at me...")
            update_records("analysis", interaction.user.id, input_name, hidden, False)
            return

        print(f"Player not found (`{input_name}`).")
        if connected:
            await interaction.response.send_message(f"Player not found (`{input_name}`). Connect to your new Minecraft username with </connect:1149442234513637448>.", ephemeral=hidden)
            update_records("analysis", interaction.user.id, input_name, hidden, False)
            return
        
        failed = True
        extra, first = get_close(input_name)

        if not first:
            await interaction.response.send_message(f"Player not found (`{input_name}`).", ephemeral=hidden)
            update_records("analysis", interaction.user.id, input_name, hidden, False)
            return
        else:
            print(f"\nAutocorrected to {first}.")
            response = requests.get(f"https://mcsrranked.com/api/users/{first}", headers=HEADERS).json()

            if response["status"] == "error":
                print("Player changed username.")
                extra = " This player may have changed username."
                await interaction.response.send_message(f"Player not found (`{input_name}`). {extra}", ephemeral=hidden)
                update_records("analysis", interaction.user.id, input_name, hidden, False)
                return
        
    await interaction.response.defer(ephemeral=hidden)
    response = response["data"]
    
    old_input = input_name
    input_name = response["nickname"]
    
    cooldown = 60 * 60 * 1 # 1 hour cooldown
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
        await interaction.followup.send(f"This command is on cooldown for `{input_name}`. (You can use it {next_available}){cd_extra}", ephemeral=hidden)
        update_records("analysis", interaction.user.id, input_name, hidden, False)
        return

    num_comps, detailed_matches = await games.get_detailed_matches(response, season, 5, 150)

    if detailed_matches == -1:
        print("Player does not have enough completions.")
        await interaction.followup.send(f"{input_name} needs a minimum of 5 completions from season {season} to analyse. (Has {num_comps})", ephemeral=hidden)
        update_records("analysis", interaction.user.id, input_name, hidden, False)
        return

    try:
        anal = analysing.main(response, num_comps, detailed_matches, season)
    except Exception as e:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls", ephemeral=hidden)
        update_records("analysis", interaction.user.id, input_name, hidden, False)
        return

    head, comments, split_polygon, ow_polygon = anal

    embed_general = nextcord.Embed(
        title = comments["general"]["title"],
        description = comments["general"]["description"],
        colour = nextcord.Colour.yellow(),
    )
    embed_split = nextcord.Embed(
        title = comments["splits"]["title"],
        description = comments["splits"]["description"],
        colour = nextcord.Colour.yellow(),
    )
    embed_ow = nextcord.Embed(
        title = comments["ow"]["title"],
        description = comments["ow"]["description"],
        colour = nextcord.Colour.yellow(),
        timestamp = datetime.now(timezone.utc)
    )
    
    embed_general.set_thumbnail(url=head)
    embed_general.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)

    split_polygon.save("split.png")
    split_file = File("split.png", filename="split.png")
    embed_split.set_image(url="attachment://split.png")

    ow_polygon.save("ow.png")
    ow_file = File("ow.png", filename="ow.png")
    embed_ow.set_image(url="attachment://ow.png")
    embed_ow.set_footer(text="Bot made by @Nadoms // Feedback appreciated :3", icon_url="https://cdn.discordapp.com/avatars/298936021557706754/a_60fb14a1dbfb0d33f3b02cc33579dacf?size=256")

    for general_key in comments["general"]:
        if general_key == "title" or general_key == "description":
            continue
        elif len(comments['general'][general_key]) == 1:
            value = ""
        elif general_key != "ffl":
            value = f"➢ {comments['general'][general_key][1]}\n➢ {comments['general'][general_key][2]}"
        else:
            value = comments['general'][general_key][1]

        if general_key == "sb":
            embed_general.add_field(
                name = "",
                value = "",
                inline = False
            )

        embed_general.add_field(
            name = comments['general'][general_key][0],
            value = value,
            inline = True
        )

    for split_key in comments["splits"]:
        if split_key == "title" or split_key == "description":
            continue
        elif split_key == "player_deaths" or split_key == "rank_deaths":
            embed_split.add_field(
                name = comments["splits"][split_key]["name"],
                value = "\n".join(comments["splits"][split_key]["value"]),
                inline = True
            )
        else:
            embed_split.add_field(
                name = comments["splits"][split_key]["name"],
                value = comments["splits"][split_key]["value"],
                inline = False
            )

    for ow_key in comments["ow"]:
        if ow_key == "title" or ow_key == "description":
            continue
        embed_ow.add_field(
            name = comments["ow"][ow_key]["name"],
            value = comments["ow"][ow_key]["value"],
            inline = False
        )

    jump_url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.id}"
    set_cooldown(jump_url, input_name)

    if failed:
        await interaction.followup.send(f"Player not found (`{old_input}`). {extra}", files=[split_file, ow_file], embeds=[embed_general, embed_split, embed_ow], ephemeral=hidden)
        update_records("analysis", interaction.user.id, input_name, hidden, True)
    else:
        await interaction.followup.send(files=[split_file, ow_file], embeds=[embed_general, embed_split, embed_ow], ephemeral=hidden)
        update_records("analysis", interaction.user.id, input_name, hidden, True)


@bot.slash_command(name="race", description="Produces a chart on your most recent race, or the race specified.")
async def race(interaction: Interaction, race_no: str = SlashOption(
    "race_no",
    required = False,
    description="The xth weekly race to get. Should be an integer.",
    default=""
    )):

    input_name = get_name(interaction)
    if race_no and race_no[0] == "#":
        race_no = race_no[1:]

    print(f"\nFinding details about weekly race #{race_no}")
    response = requests.get(f"https://mcsrranked.com/api/weekly-race/{race_no}", headers=HEADERS).json()

    if response["status"] == "error":
        if response["data"] == "Too many requests":
            await interaction.response.send_message(f"Too many commands have been issued! The Ranked API is cooling down...")
            print(f"\nRanked API is mad at me...")
            update_records("race", interaction.user.id, race_no, False, False)
            return

        latest_response = requests.get(f"https://mcsrranked.com/api/weekly-race", headers=HEADERS).json()
        latest_race = latest_response["data"]["id"]
        print("Race not found.")
        await interaction.response.send_message(f"Weekly race not found. (`{race_no}`)\nThe latest race was weekly race #{latest_race}")
        update_records("race", interaction.user.id, race_no, False, False)
        return
    
    response = response["data"]
    
    await interaction.response.defer()
    
    try:
        race_embed = racing.main(response, input_name)
    except Exception as e:
        print("Error caught!")
        traceback.print_exc()
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls")
        update_records("race", interaction.user.id, race_no, False, False)
        return

    await interaction.followup.send(embed=race_embed)
    update_records("race", interaction.user.id, race_no, False, True)


@bot.slash_command(name="customise", description="Allows you to personalise your card. Only applies to connected users.")
async def customise(interaction: Interaction, background: str = SlashOption(
    "background",
    required = True,
    description="Your background of choice for your card.",
    default="Classic",
    choices=["Classic", "Overworld", "Bastion", "Fortress", "Portal", "Stronghold", "The End"]
    ), hidden: str = SlashOption(
    "hidden",
    required = False,
    description="Hides my response..",
    default="",
    choices=["True"]
    )):
    
    if hidden:
        hidden = True
    else:
        hidden = False
        
    input_name = get_name(interaction)
    if not input_name:
        await interaction.response.send_message("Please connect your minecraft account to your discord with </connect:1149442234513637448> to customise your card.", ephemeral=hidden)
        update_records("background", interaction.user.id, background, hidden, False)
        return
    
    uid = str(interaction.user.id)
    bg_mapping = {
        "Classic": "grass.jpg",
        "Overworld": "beach.jpg",
        "Bastion": "bastion.jpg",
        "Fortress": "fort.jpg",
        "Portal": "portal.jpg",
        "Stronghold": "stronghold.jpg",
        "The End": "end.jpg"}

    file = path.join("src", "database", "users.json")
    with open (file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if uid == user["discord"]:
            user["background"] = bg_mapping[background]
            user_exists = True
            break
        
    if not user_exists:
        await interaction.response.send_message("An error has occurred. <@298936021557706754> fix it pls", ephemeral=hidden)
        update_records("background", interaction.user.id, background, hidden, False)
        return

    with open (file, "w") as f:
        users_json = json.dumps(users, indent=4)
        f.write(users_json)
    
    await interaction.response.send_message(f"Updated your card background to {background}!", ephemeral=hidden)
    update_records("background", interaction.user.id, background, hidden, True)
    return


@bot.slash_command(name="connect", description="Connects your minecraft account with your discord account.")
async def connect(interaction: Interaction, input_name: str):
    
    uid = str(interaction.user.id)
    user_exists = False
    user_id = 0
    
    file = path.join("src", "database", "users.json")
    with open (file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if uid == user["discord"]:
            user_exists = True
            user_id = users["users"].index(user)
        elif input_name.lower() == user["minecraft"].lower():
            await interaction.response.send_message(f"`{input_name}` is already connected to {bot.get_user(int(user['discord']))}.")
            update_records("connect", interaction.user.id, input_name, False, False)
            return

    if not user_exists:
        new_user = {
            "minecraft": input_name,
            "discord": uid,
            "background": "grass.jpg",
            "cooldown": 0,
            "last_link": ""
        }
        users["users"].append(new_user)
    else:
        users["users"][user_id]["minecraft"] = input_name

    with open (file, "w") as f:
        users_json = json.dumps(users, indent=4)
        f.write(users_json)
    
    await interaction.response.send_message(f"`{input_name}` has been connected to your discord!")
    update_records("connect", interaction.user.id, input_name, False, not user_exists)
    return


@bot.slash_command(name="disconnect", description="Disconnects your minecraft account from your discord account.")
async def disconnect(interaction: Interaction):
    
    uid = str(interaction.user.id)
    
    file = path.join("src", "database", "users.json")
    with open (file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if uid == user["discord"]:
            users["users"].remove(user)

            with open (file, "w") as f:
                print(users)
                users_json = json.dumps(users, indent=4)
                f.write(users_json)
            await interaction.response.send_message(f"`{user['minecraft']}` has been disconnected from your discord.")
            update_records("disconnect", interaction.user.id, user['minecraft'], False, True)
            return
        
    await interaction.response.send_message(f"You are not connected. Please connect your minecraft account with </connect:1149442234513637448> to your discord.")
    update_records("disconnect", interaction.user.id, "Unknown", False, False)


@bot.slash_command(name="help", description="Don't know where to start?")
async def help(interaction: Interaction,
    hidden: str = SlashOption(
    "hidden",
    required = False,
    description="Hides my response.",
    default="",
    choices=["True"]
    )):
    
    if hidden:
        hidden = True
    else:
        hidden = False

    embed = nextcord.Embed(
        title = "Ranked Cards - Help and Commands",
        description = "Thanks for using the MCSR Ranked Cards bot, made by @Nadoms. Any questions, just dm me :)\nThese are the current available commands:",
        colour = nextcord.Colour.yellow()
    )
    
    embed.set_thumbnail(url=r"https://mcsrranked.com/_next/image?url=%2Ftest1.png&w=640&q=75")
    embed.add_field(
        name = "/card",
        value = "`Options: Minecraft username, hide response`\n`Defaults: Connected user, public`\nGenerates the ***statistics card*** for the player that you input.",
        inline = False
    )
    embed.add_field(
        name = "/plot",
        value = "`Options: Minecraft username, type of data [Elo / Completion time], season [Lifetime/1/2/3/4/5], hide response`\n`Defaults: Connected user, Elo, S4, public`\n***Plots a graph*** for the type of data (Elo / Completion time) across the timeframe (Season 1/2/3/4 / Lifetime) and for the player you specify.",
        inline = False
    )
    embed.add_field(
        name = "/match",
        value = "`Options: Match ID, hide response`\n`Defaults: Last ranked match played, public`\n***Draws a chart*** visualising two player's splits in a game.",
        inline = False
    )
    embed.add_field(
        name = "/analysis",
        value = "`Options: Minecraft username, hide response`\n`Defaults: Connected user, public`\n***Analyses your games*** to give feedback about splits and overworlds.",
        inline = False
    )
    embed.add_field(
        name = "/customise",
        value = "`Options: Card background, hide response`\n`Defaults: Classic, public`\n***Customises your card*** how you specify, currently with the background.",
        inline = False
    )
    embed.add_field(
        name = "/connect",
        value = "`Options: Minecraft username`\n***Connects your discord account*** to a Minecraft username so that you don't have to write it when doing the other commands.",
        inline = False
    )
    embed.add_field(
        name = "/disconnect",
        value = "***Removes the connected Minecraft account*** from your discord, useful if you changed name or switched account.",
        inline = False
    )
    
    await interaction.send(embed=embed, ephemeral=hidden)
    update_records("help", interaction.user.id, "None", hidden, True)


def get_user_info(response, input_name):
    file = path.join("src", "database", "users.json")
    with open (file, "r") as f:
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
    with open (file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if uid == user["discord"]:
            return user["minecraft"]
    
    return ""


def get_cooldown(input_name):
    file = path.join("src", "database", "users.json")
    with open (file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if input_name == user["minecraft"]:
            return user["cooldown"], user["last_link"]
    
    return False, False


def set_cooldown(jump_url, input_name):
    file = path.join("src", "database", "users.json")
    with open (file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if input_name == user["minecraft"]:
            user["cooldown"] = int(time())
            user["last_link"] = jump_url
            break
        
    with open (file, "w") as f:
        users_json = json.dumps(users, indent=4)
        f.write(users_json)


def get_close(input_name):
    extra = ""
    first = None

    file = path.join("src", "database", "players.txt")
    with open(file, "r") as f:
        players = f.readlines()
        close = difflib.get_close_matches(input_name, players)
    if close:
        first = close[0].strip()
        extra += f" Autocorrected to `{first}`"
        
        if len(close) > 1:
            extra += ", but you may have also meant "
            
        for i in range(1, len(close)):
            player = close[i].strip()
            extra += f"`{player}`"
            if i < len(close) - 2:
                extra += ", "
            elif i == len(close) - 2:
                extra += " or "
        extra += "."

    return [extra, first]


def update_records(command, caller, callee, hidden, completed):
    if updates_disabled:
        return
    calls_file = path.join("src", "database", "calls.csv")
    stats_file = path.join("src", "database", "stats.json")

    with open(calls_file, "a") as f:
        row = f"\n{command},{caller},{callee},{int(time())},{hidden},{completed}"
        f.write(row)

    with open(stats_file, "r") as f:
        stats = json.load(f)

    stats["stats"]["totalCommands"] += 1

    if command == "card":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["cards"]["success"] += completed
        stats["stats"]["cards"]["fail"] += 1-completed
    
    elif command == "plot":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["plots"]["success"] += completed
        stats["stats"]["plots"]["fail"] += 1-completed
    
    elif command == "match":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["matches"]["success"] += completed
        stats["stats"]["matches"]["fail"] += 1-completed
    
    elif command == "analysis":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["analyses"]["success"] += completed
        stats["stats"]["analyses"]["fail"] += 1-completed
    
    elif command == "connect":
        stats["stats"]["connectedUsers"] += 1
        stats["stats"]["connects"]["success"] += completed
        stats["stats"]["connects"]["fail"] += 1-completed

    elif command == "disconnect":
        stats["stats"]["connectedUsers"] -= 1
        stats["stats"]["disconnects"]["success"] += completed
        stats["stats"]["disconnects"]["fail"] += 1-completed

    elif command == "help":
        stats["stats"]["helps"] += 1

    elif command == "background":
        stats["stats"]["backgrounds"] += 1

    if hidden:
        stats["stats"]["totalHidden"] += 1

    with open (stats_file, "w") as f:
        stats_json = json.dumps(stats, indent=4)
        f.write(stats_json)

load_dotenv()
updates_disabled = True
bot.run(getenv("TEST_TOKEN"))