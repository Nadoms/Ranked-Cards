import nextcord
from nextcord import File, Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands
from PIL import Image
from os import getenv
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
async def card(ctx, input_name):
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
    with open (r"src\link.txt", "r") as f:
        for line in f:
            if input_name.lower() == line.split(":")[0].lower():
                discord = line.split(":")[-1]
                id = nextcord.utils.get(bot.get_all_members(), name=discord).id
                break
        else:
            id = "343108228890099713"
    return id

@bot.command()
async def register(ctx, input_name):
    user = str(ctx.message.author)
    if user[-2:] == "#0":
        user = user[:-2]
    user_exists = False
    with open(r"src\link.txt", "r") as f:
        for line in f:
            mcname = line.split(":")[0]
            username = line.split(":")[-1]
            if user == username:
                user_exists = True
                await ctx.send(f"You are already linked to {mcname}.")
            elif input_name.lower() == mcname.lower():
                user_exists = True
                await ctx.send(f"{input_name} is already linked to {username}.")
    if not user_exists:
        with open (r"src\link.txt", "a") as f:
            f.write(f"\n{input_name}:{user}")
        await ctx.send(f"{input_name} has been linked to your discord!")

@bot.command()
async def unregister(ctx, input_name):
    user = str(ctx.message.author)
    if user[-2:] == "#0":
        user = user[:-2]
    with open(r"src\link.txt", "r") as f:
        lines = f.readlines()
    with open(r"src\link.txt", 'w') as f:
        unlinked = False
        for line in lines:
            mcname = line.split(":")[0]
            username = line.split(":")[-1]
            if not (input_name.lower() == mcname.lower() and user == username):
                f.write(line)
            else:
                unlinked = True
        if unlinked:
            await ctx.send(f"{input_name} has been unlinked from your discord.")
        else:
            await ctx.send(f"You are not linked to {input_name}.")

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