import difflib
import nextcord
import json
from nextcord import File, Interaction, SlashOption, Embed, Colour
from nextcord.ext import commands
from os import getenv, path
from dotenv import load_dotenv
from time import time

import requests
from commands import card as carding
from commands import graph as graphing
from commands import analyse as analysing
from gen_functions import match

intents = intents=nextcord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="=", intents=intents, default_guild_ids=[735859906434957392, 1113914901325434880, 1056779246728658984])

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
    description="Makes it so only you can see it.",
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
        if input_name:
            connected = True
    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}", headers=headers).json()
    
    print(f"\nGenerating card for {input_name}")
    failed = False
    if response["status"] == "error":
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
            response = requests.get(f"https://mcsrranked.com/api/users/{first}", headers=headers).json()

            if response["status"] == "error":
                print("Player changed username.")
                extra = " This player may have changed username."
                await interaction.response.send_message(f"Player not found (`{input_name}`). {extra}", ephemeral=hidden)
                update_records("card", interaction.user.id, input_name, hidden, False)
                return
        
    input_name = response["data"]["nickname"]
    uid, background = get_user_info(response, input_name)
    user = await bot.fetch_user(uid)
    pfp = user.avatar
    if not pfp:
        pfp = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"
    discord = str(user)
    if discord[-2:] == "#0":
        discord = discord[:-2]
    await interaction.response.defer(ephemeral=hidden)
    
    try:
        img = carding.main(input_name, response, discord, pfp, background)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls", ephemeral=hidden)
        update_records("card", interaction.user.id, input_name, hidden, False)
        return

    img.save("card.png")
    with open("card.png", "rb") as f:
        img = File(f)
    if failed:
        await interaction.followup.send(f"Player not found (`{input_name}`). {extra}", files=[img], ephemeral=hidden)
        update_records("card", interaction.user.id, input_name, hidden, True)
    else:
        await interaction.followup.send(files=[img], ephemeral=hidden)
        update_records("card", interaction.user.id, input_name, hidden, True)


@bot.slash_command(name="connect", description="Connects your minecraft account with your discord account.")
async def connect(interaction: Interaction, input_name: str):
    
    uid = str(interaction.user.id)
    user_exists = False
    
    file = path.join("src", "database", "users.json")
    with open (file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if uid == user["discord"]:
            user_exists = True
        elif input_name.lower() == user["minecraft"].lower():
            await interaction.response.send_message(f"`{input_name}` is already connected to {bot.get_user(int(user['discord']))}.")
            update_records("connect", interaction.user.id, input_name, False, False)
            return

    if not user_exists:
        new_user = {
            "minecraft": input_name,
            "discord": uid,
            "background": "grass.jpg"
        }
        users["users"].append(new_user)
    else:
        user["minecraft"] = input_name

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
    default="5",
    choices=["1", "2", "3", "4", "5", "Lifetime"]
    ), hidden: str = SlashOption(
    "hidden",
    required = False,
    description="Makes it so only you can see it.",
    default="",
    choices=["True"]
    )):
    
    if hidden:
        hidden = True
    else:
        hidden = False
        
    if not input_name:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message("Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a minecraft username.", ephemeral=hidden)
            update_records("plot", interaction.user.id, "Unknown", hidden, False)
            return
    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}", headers=headers).json()
        
    print(f"\nDrawing {type} graph for {input_name}")
    failed = False
    if response["status"] == "error":
        print(f"Player not found  (`{input_name}`).")
        failed = True
        extra, first = get_close(input_name)

        if not first:
            await interaction.response.send_message(f"Player not found  (`{input_name}`).", ephemeral=hidden)
            update_records("plot", interaction.user.id, input_name, hidden, False)
            return
        else:
            print(f"\nAutocorrected to {first}.")
            response = requests.get(f"https://mcsrranked.com/api/users/{first}", headers=headers).json()

            if response["status"] == "error":
                print("Player changed username.")
                extra = " This player may have changed username."
                await interaction.response.send_message(f"Player not found (`{input_name}`). {extra}", ephemeral=hidden)
                update_records("plot", interaction.user.id, input_name, hidden, False)
                return
    
    input_name = response["data"]["nickname"]
    await interaction.response.defer(ephemeral=hidden)
    
    try:
        img = graphing.main(input_name, response, type, season)
    except Exception as e:
        print(e)
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
        await interaction.followup.send(f"Player not found (`{input_name}`). {extra}", files=[img], ephemeral=hidden)
        update_records("plot", interaction.user.id, input_name, hidden, True)
    else:
        await interaction.followup.send(files=[img], ephemeral=hidden)
        update_records("plot", interaction.user.id, input_name, hidden, True)


@bot.slash_command(name="help", description="Don't know where to start?")
async def help(interaction: Interaction,
    hidden: str = SlashOption(
    "hidden",
    required = False,
    description="Makes it so only you can see it.",
    default="",
    choices=["True"]
    )):
    
    if hidden:
        hidden = True
    else:
        hidden = False

    embed = nextcord.Embed(
        title = "Ranked Cards - Help and Commands",
        description = "Thank you for using the MCSR Ranked Cards bot, made by Nadoms. Any questions, just dm me :)\nThese are the current available commands:",
        colour = nextcord.Colour.yellow()
    )
    
    embed.set_thumbnail(url=r"https://mcsrranked.com/_next/image?url=%2Ftest1.png&w=640&q=75")
    embed.add_field(
        name = "/card",
        value = "`Options: Minecraft username, hide card`\n`Defaults: Connected user, public`\nGenerates the ***statistics card*** for the player that you input",
        inline = False
    )
    embed.add_field(
        name = "/plot",
        value = "`Options: Minecraft username, type of data [Elo / Completion time], season [Lifetime / 1/2/3/4], hide graph`\n`Defaults: Connected user, Elo, S4, public`\n***Plots a graph*** for the type of data (Elo / Completion time) across the timeframe (Season 1/2/3/4 / Lifetime) and for the player you specify",
        inline = False
    )
    embed.add_field(
        name = "/analyse",
        value = "`Options: Match ID`\nMatch analysis command to be ***coming soon***...",
        inline = False
    )
    embed.add_field(
        name = "/connect",
        value = "`Options: Minecraft username`\n***Connects your discord account*** to a Minecraft username so that you don't have to write it when doing the other commands",
        inline = False
    )
    embed.add_field(
        name = "/disconnect",
        value = "***Removes the connected Minecraft account*** from your discord, useful if you changed name or switched account",
        inline = False
    )
    
    await interaction.send(embed=embed, ephemeral=hidden)
    update_records("help", interaction.user.id, "None", hidden, False)


@bot.slash_command(name="analyse", description="Performs an analysis on your most recent match, or the match specified.")
async def analyse(interaction: Interaction, match_id: str = SlashOption(
    "match_id",
    required = False,
    description="The match to perform an analysis on.",
    default=None
    ), hidden: str = SlashOption(
    "hidden",
    required = False,
    description="Makes it so only you can see it.",
    default="",
    choices=["True"]
    )):
    
    if hidden:
        hidden = True
    else:
        hidden = False

    input_name = get_name(interaction)
    uuid = None
    if not match_id:
        if not input_name:
            await interaction.response.send_message("Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a match ID.")
            update_records("analyse", interaction.user.id, "Unknown", hidden, False)
            return

        print(f"\nFinding {input_name}'s last match")
        uuid, match_id = match.get_last_match(input_name)
        if not match_id:
            await interaction.response.send_message("Player has no matches from this season.")
            update_records("analyse", interaction.user.id, match_id, hidden, False)
            return

    print(f"\nAnalysing match {match_id}")
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = requests.get(f"https://mcsrranked.com/api/matches/{match_id}", headers=headers).json()
    if response["status"] == "error":
        print("Match not found.")
        await interaction.response.send_message("Match not found.")
        update_records("analyse", interaction.user.id, match_id, hidden, False)
        return
    
    await interaction.response.defer()
    
    try:
        img = analysing.main(response, match_id)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls")
        update_records("analyse", interaction.user.id, match_id, hidden, False)
        return

    img.save("analysis.png")
    with open("analysis.png", "rb") as f:
        img = File(f)
    await interaction.followup.send(files=[img])
    update_records("analyse", interaction.user.id, match_id, hidden, True)
    

def get_user_info(response, input_name):
    file = path.join("src", "database", "users.json")
    with open (file, "r") as f:
        users = json.load(f)

    for user in users["users"]:
        if input_name.lower() == user["minecraft"].lower():
            return user["discord"], user["background"]
        
    if "discord" in response["data"]["connections"]:
        uid = response["data"]["connections"]["discord"]["id"]
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
    calls_file = path.join("src", "database", "calls.csv")
    stats_file = path.join("src", "database", "stats.json")

    with open(calls_file, "a") as f:
        row = f"\n{command},{caller},{callee},{int(time())},{hidden}"
        f.write(row)

    with open(stats_file, "r") as f:
        stats = json.load(f)

    stats["stats"]["totalCommands"] += 1

    if command == "card":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["cards"]["success"] += completed
        stats["stats"]["cards"]["fail"] += 1-completed
    
    if command == "plot":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["plots"]["success"] += completed
        stats["stats"]["plots"]["fail"] += 1-completed
    
    if command == "analyse":
        stats["stats"]["totalGenerated"] += 1
        stats["stats"]["analyses"]["success"] += completed
        stats["stats"]["analyses"]["fail"] += 1-completed
    
    if command == "connect":
        stats["stats"]["connectedUsers"] += 1
        stats["stats"]["connects"]["success"] += completed
        stats["stats"]["connects"]["fail"] += 1-completed

    if command == "disconnect":
        stats["stats"]["connectedUsers"] -= 1
        stats["stats"]["disconnects"]["success"] += completed
        stats["stats"]["disconnects"]["fail"] += 1-completed

    if command == "help":
        stats["stats"]["helps"] += 1

    if hidden:
        stats["stats"]["totalHidden"] += 1

    with open (stats_file, "w") as f:
        stats_json = json.dumps(stats, indent=4)
        f.write(stats_json)


load_dotenv()
bot.run(getenv("TEST_TOKEN"))