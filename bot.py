import nextcord
from nextcord import File, Interaction
from nextcord.ext import commands
from os import getenv, path
from dotenv import load_dotenv

import card as carding

bot = commands.Bot(command_prefix="=", intents=nextcord.Intents.all(), default_guild_ids=[735859906434957392, 1056779246728658984])

@bot.event
async def on_ready():
    print("Bot is running")

@bot.command()
async def ping(ctx):
    print("hello")
    await ctx.send("hi there")

@bot.command()
async def card(ctx, *input_name):
    if not input_name:
        input_name = get_name(ctx)
        if input_name == "":
            await ctx.send("Please register your minecraft account with =register.")
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

def get_name(ctx):
    file = path.join("src", "link.txt")
    user = str(ctx.message.author)
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

@bot.command()
async def register(ctx, input_name):
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
async def unregister(ctx):
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
            await ctx.send(f"You are not registered. Please register your minecraft account with =register.")

@bot.slash_command(name="ping")
async def ping(interaction: Interaction):
    print("hi")
    await interaction.response.send_message("Pong!")

@bot.slash_command(name="card", description="Generates a card for the player you specify.")
async def card(interaction: Interaction, input_name: str):
    await interaction.response.send_message(f"hi! {input_name}")

@bot.slash_command(name="register", description="Links your minecraft account with your discord account.")
async def register(interaction: Interaction, input_name: str):
    await interaction.response.send_message(f"hi! {input_name}")

@bot.slash_command(name="unregister", description="Unlinks your minecraft account with your discord account.")
async def unregister(interaction: Interaction, input_name: str):
    await interaction.response.send_message(f"hi! {input_name}")

load_dotenv()
bot.run(getenv("DISCORD_TOKEN"))