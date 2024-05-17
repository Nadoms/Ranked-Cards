import difflib
import nextcord
from nextcord import File, Interaction, SlashOption, Embed, Colour
from nextcord.ext import commands
from os import getenv, path
from dotenv import load_dotenv

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
        
    if not input_name:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message("Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a minecraft username.", ephemeral=hidden)
            return
    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}", headers=headers).json()
    
    print(f"\nGenerating card for {input_name}")
    failed = False
    if response["status"] == "error":
        print("Player not found.")
        failed = True
        extra, first = get_close(input_name)

        if not first:
            await interaction.response.send_message("Player not found.", ephemeral=hidden)
            return
        else:
            print(f"\nAutocorrected to {first}.")
            response = requests.get(f"https://mcsrranked.com/api/users/{first}", headers=headers).json()

            if response["status"] == "error":
                print("Player changed username.")
                extra = " This player may have changed username."
                await interaction.response.send_message("Player not found." + extra, ephemeral=hidden)
                return
        
    input_name = response["data"]["nickname"]
    user = await bot.fetch_user(get_uid(response, input_name))
    pfp = user.avatar
    if not pfp:
        pfp = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"
    discord = str(user)
    if discord[-2:] == "#0":
        discord = discord[:-2]
    await interaction.response.defer(ephemeral=hidden)
    
    try:
        img = carding.main(input_name, response, discord, pfp)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls", ephemeral=hidden)

    img.save("card.png")
    with open("card.png", "rb") as f:
        img = File(f)
    if failed:
        await interaction.followup.send("Player not found." + extra, files=[img], ephemeral=hidden)
    else:
        await interaction.followup.send(files=[img], ephemeral=hidden)


@bot.slash_command(name="connect", description="Connects your minecraft account with your discord account.")
async def connect(interaction: Interaction, input_name: str):
    file = path.join("src", "connect.txt")

    uid = str(interaction.user.id)

    '''user = str(interaction.user)
    if user[-2:] == "#0":
        user = user[:-2]'''

    user_exists = False
    mc_exists = False

    with open (file, "r") as f:
        for line in f:
            mcname = line.split(":")[0].strip()
            storeduid = line.split(":")[-1].strip()

            if uid == storeduid:
                user_exists = True
                break
            elif input_name.lower() == mcname.lower():
                mc_exists = True
                await interaction.response.send_message(f"`{input_name}` is already connected to {bot.get_user(int(storeduid))}.")

    if user_exists:
        with open (file, "r") as f:
            lines = f.readlines()

        with open (file, 'w') as f:
            for line in lines:
                mcname = line.split(":")[0].strip()
                storeduid = line.split(":")[-1].strip()
                if uid != storeduid:
                    f.write(line)
                else:
                    f.write(f"{input_name}:{uid}\n")
        await interaction.response.send_message(f"`{input_name}` has been connected to your discord!")

    elif not mc_exists:
        with open (file, "a") as f:
            f.write(f"{input_name}:{uid}\n")
        await interaction.response.send_message(f"`{input_name}` has been connected to your discord!")


@bot.slash_command(name="disconnect", description="Disconnects your minecraft account with your discord account.")
async def disconnect(interaction: Interaction):
    file = path.join("src", "connect.txt")

    uid = str(interaction.user.id)

    '''user = str(interaction.user)
    if user[-2:] == "#0":
        user = user[:-2]'''
    
    with open (file, "r") as f:
        lines = f.readlines()

    with open (file, 'w') as f:
        disconnected = False
        my_mcname = ""

        for line in lines:
            mcname = line.split(":")[0].strip()
            storeduid = line.split(":")[-1].strip()
            if uid != storeduid:
                f.write(line)
            else:
                disconnected = True
                mymcname = mcname

        if disconnected:
            await interaction.response.send_message(f"`{mymcname}` has been disconnected from your discord.")
        else:
            await interaction.response.send_message(f"You are not connected. Please connect your minecraft account with </connect:1149442234513637448> to your discord.")


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
            return
    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}", headers=headers).json()
        
    print(f"\nDrawing {type} graph for {input_name}")
    failed = False
    if response["status"] == "error":
        print("Player not found.")
        failed = True
        extra, first = get_close(input_name)

        if not first:
            await interaction.response.send_message("Player not found.", ephemeral=hidden)
            return
        else:
            print(f"\nAutocorrected to {first}.")
            response = requests.get(f"https://mcsrranked.com/api/users/{first}", headers=headers).json()

            if response["status"] == "error":
                print("Player changed username.")
                extra = " This player may have changed username."
                await interaction.response.send_message("Player not found." + extra, ephemeral=hidden)
                return
    
    input_name = response["data"]["nickname"]
    await interaction.response.defer(ephemeral=hidden)
    
    try:   
        img = graphing.main(input_name, response, type, season)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls", ephemeral=hidden)
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
        return

    img.save("graph.png")
    with open("graph.png", "rb") as f:
        img = File(f)
    if failed:
        await interaction.followup.send("Player not found." + extra, files=[img], ephemeral=hidden)
    else:
        await interaction.followup.send(files=[img], ephemeral=hidden)


@bot.slash_command(name="help", description="Don't know where to start?")
async def help(interaction: Interaction):

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
    
    await interaction.send(embed=embed)


@bot.slash_command(name="analyse", description="Performs an analyses on your most recent match, or the match specified.")
async def analyse(interaction: Interaction, match_id: str = SlashOption(
    "match_id",
    required = False,
    description="The match to perform an analysis on.",
    default=None
    )):

    input_name = get_name(interaction)
    uuid = None
    if not match_id:
        if not input_name:
            await interaction.response.send_message("Please connect your minecraft account to your discord with </connect:1149442234513637448> or specify a match ID.")
            return

        print(f"\nFinding {input_name}'s last match")
        uuid, match_id = match.get_last_match(input_name)
        if not match_id:
            await interaction.response.send_message("Player has no matches from this season.")
            return

    print(f"\nAnalysing match {match_id}")
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = requests.get(f"https://mcsrranked.com/api/matches/{match_id}", headers=headers).json()
    if response["status"] == "error":
        print("Match not found.")
        await interaction.response.send_message("Match not found.")
        return
    
    await interaction.response.defer()
    
    try:
        img = analysing.main(response, match_id)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls")
        return

    img.save("analysis.png")
    with open("analysis.png", "rb") as f:
        img = File(f)
    await interaction.followup.send(files=[img])


def get_uid(response, input_name):
    if "discord" in response["data"]["connections"]:
        uid = response["data"]["connections"]["discord"]["id"]
        return uid
    file = path.join("src", "connect.txt")
    with open (file, "r") as f:
        for line in f:
            if input_name.lower() == line.split(":")[0].lower():
                uid = line.split(":")[-1]
                break
        else:
            uid = "343108228890099713"
    return uid

def get_name(interaction_ctx):
    file = path.join("src", "connect.txt")
    try:
        uid = str(interaction_ctx.user.id)
    except:
        uid = str(interaction_ctx.message.author.id)
    with open (file, "r") as f:
        for line in f:
            mcname = line.split(":")[0].strip()
            storeduid = line.split(":")[-1].strip()
            if uid == storeduid:
                return mcname
        else:
            return ""

def get_close(input_name):
    extra = ""
    first = None

    file = path.join("src", "players.txt")
    with open(file) as f:
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


load_dotenv()
bot.run(getenv("TEST_TOKEN"))