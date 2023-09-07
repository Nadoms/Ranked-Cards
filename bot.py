import nextcord
from nextcord import File, Interaction, SlashOption
from nextcord.ext import commands
from os import getenv, path
from dotenv import load_dotenv

import card as carding
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
)):
    if not input_name:
        input_name = get_name(interaction)
        if not input_name:
            await interaction.response.send_message("Please link your minecraft account with </link:1145666604567367750> or specify a minecraft username.")
            return
        
    print(f"\nGenerating card for {input_name}")
    user = await bot.fetch_user(get_uid(input_name))
    pfp = user.avatar
    discord = str(user)
    if discord[-2:] == "#0":
        discord = discord[:-2]
    await interaction.response.defer()

    try:
        img = carding.__main__(input_name, discord, pfp)
    except Exception as e:
        await interaction.followup.send("An error has occurred. <@298936021557706754> fix it pls")
    if img:
        img.save("card.png")
        with open("card.png", "rb") as f:
            img = File(f)
        await interaction.channel.send(files=[img])
        await interaction.followup.send(f"{input_name}'s ranked card:")
    else:
        await interaction.followup.send("Player not found.")

@bot.slash_command(name="link", description="Links your minecraft account with your discord account.")
async def link(interaction: Interaction, input_name: str):
    file = path.join("src", "link.txt")

    uid = str(interaction.user.id)

    '''user = str(interaction.user)
    if user[-2:] == "#0":
        user = user[:-2]'''

    user_exists = False

    with open (file, "r") as f:
        for line in f:
            mcname = line.split(":")[0].strip()
            storeduid = line.split(":")[-1].strip()

            if uid == storeduid:
                user_exists = True
                await interaction.response.send_message(f"You are already linked to {mcname}.")
            elif input_name.lower() == mcname.lower():
                user_exists = True
                await interaction.response.send_message(f"{input_name} is already linked to {bot.get_user(int(storeduid))}.")

    if not user_exists:
        with open (file, "a") as f:
            f.write(f"\n{input_name}:{uid}")
        await interaction.response.send_message(f"{input_name} has been linked to your discord!")

@bot.slash_command(name="unlink", description="Unlinks your minecraft account with your discord account.")
async def unlink(interaction: Interaction):
    file = path.join("src", "link.txt")

    uid = str(interaction.user.id)

    '''user = str(interaction.user)
    if user[-2:] == "#0":
        user = user[:-2]'''
    
    with open (file, "r") as f:
        lines = f.readlines()

    with open (file, 'w') as f:
        unlinked = False

        for line in lines:
            mcname = line.split(":")[0].strip()
            storeduid = line.split(":")[-1].strip()
            if uid != storeduid:
                f.write(line)
            else:
                unlinked = True

        if unlinked:
            await interaction.response.send_message(f"{mcname} has been unlinked from your discord.")
        else:
            await interaction.response.send_message(f"You are not linked. Please link your minecraft account with </link:1145666604567367750>.")


def get_uid(input_name):
    file = path.join("src", "link.txt")
    with open (file, "r") as f:
        for line in f:
            if input_name.lower() == line.split(":")[0].lower():
                uid = line.split(":")[-1]
                break
        else:
            uid = "343108228890099713"
    return uid

def get_name(interaction_ctx):
    file = path.join("src", "link.txt")
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

load_dotenv()
bot.run(getenv("DISCORD_TOKEN"))