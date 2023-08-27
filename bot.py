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

# PREFIX COMMANDS
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def card(ctx, *input_name):
    if not input_name:
        input_name = get_name(ctx)
        if input_name == "":
            await ctx.send("Please link your minecraft account with /link or specify a minecraft username.")
            return
    else:
        input_name = input_name[0]
    user = await bot.fetch_user(get_id(input_name))
    pfp = user.avatar
    img = carding.__main__(input_name, pfp)
    if img:
        img.save("card.png")
        with open("card.png", "rb") as f:
            img = File(f)
        await ctx.channel.send(file=img)
    else:
        await ctx.send("Player not found.")

@bot.command()
async def link(ctx, input_name):
    file = path.join("src", "link.txt")
    user = str(ctx.message.author)
    if user[-2:] == "#0":
        user = user[:-2]
    user_exists = False
    with open (file, "r") as f:
        for line in f:
            mcname = line.split(":")[0].strip()
            username = line.split(":")[-1].strip()
            if user == username:
                user_exists = True
                await ctx.send(f"You are already linked to {mcname}.")
            elif input_name.lower() == mcname.lower():
                user_exists = True
                await ctx.send(f"{input_name} is already linked to {username}.")
    if not user_exists:
        with open (file, "a") as f:
            f.write(f"\n{input_name}:{user}")
        await ctx.send(f"{input_name} has been linked to your discord!")

@bot.command()
async def unlink(ctx):
    file = path.join("src", "link.txt")
    user = str(ctx.message.author)
    if user[-2:] == "#0":
        user = user[:-2]
    with open (file, "r") as f:
        lines = f.readlines()
    with open (file, 'w') as f:
        unlinked = False
        for line in lines:
            mcname = line.split(":")[0]
            username = line.split(":")[-1]
            if not (user == username):
                f.write(line)
            else:
                unlinked = True
        if unlinked:
            await ctx.send(f"{mcname} has been unlinked from your discord.")
        else:
            await ctx.send(f"You are not linked. Please link your minecraft account with =link.")

# SLASH COMMANDS
@bot.slash_command(name="ping", description="Pong!")
async def ping(interaction: Interaction):
    await interaction.response.send_message("Pong!")

@bot.slash_command(name="card", description="Generates a card for the player you specify.")
async def card(interaction: Interaction, input_name: str = SlashOption(
    "card",
    required = False,
    default = ""
)):
    if not input_name:
        input_name = get_name(interaction)
        if input_name == "":
            await interaction.response.send_message("Please link your minecraft account with /link or specify a minecraft username.")
            return
    user = await bot.fetch_user(get_id(input_name))
    pfp = user.avatar
    await interaction.response.defer()
    img = carding.__main__(input_name, pfp)
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
    user = str(interaction.user)
    if user[-2:] == "#0":
        user = user[:-2]
    user_exists = False
    with open (file, "r") as f:
        for line in f:
            mcname = line.split(":")[0].strip()
            username = line.split(":")[-1].strip()
            if user == username:
                user_exists = True
                await interaction.response.send_message(f"You are already linked to {mcname}.")
            elif input_name.lower() == mcname.lower():
                user_exists = True
                await interaction.response.send_message(f"{input_name} is already linked to {username}.")
    if not user_exists:
        with open (file, "a") as f:
            f.write(f"\n{input_name}:{user}")
        await interaction.response.send_message(f"{input_name} has been linked to your discord!")

@bot.slash_command(name="unlink", description="Unlinks your minecraft account with your discord account.")
async def unlink(interaction: Interaction):
    file = path.join("src", "link.txt")
    user = str(interaction.user)
    if user[-2:] == "#0":
        user = user[:-2]
    with open (file, "r") as f:
        lines = f.readlines()
    with open (file, 'w') as f:
        unlinked = False
        for line in lines:
            mcname = line.split(":")[0]
            username = line.split(":")[-1]
            if not (user == username):
                f.write(line)
            else:
                unlinked = True
        if unlinked:
            await interaction.response.send_message(f"{mcname} has been unlinked from your discord.")
        else:
            await interaction.response.send_message(f"You are not linked. Please link your minecraft account with =link.")


def get_id(input_name):
    file = path.join("src", "link.txt")
    with open (file, "r") as f:
        for line in f:
            if input_name.lower() == line.split(":")[0].lower():
                discord = line.split(":")[-1]
                id = nextcord.utils.get(bot.get_all_members(), name=discord).id
                break
        else:
            id = "343108228890099713"
    return id

def get_name(interaction_ctx):
    file = path.join("src", "link.txt")
    try:
        user = str(interaction_ctx.user)
    except:
        user = str(interaction_ctx.message.author)
    if user[-2:] == "#0":
        user = user[:-2]
    with open (file, "r") as f:
        for line in f:
            mcname = line.split(":")[0].strip()
            username = line.split(":")[-1].strip()
            if user == username:
                return mcname
        else:
            return ""

load_dotenv()
bot.run(getenv("DISCORD_TOKEN"))