import nextcord
from nextcord import File, Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands
from PIL import Image
from os import getenv

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
    img = carding.__main__(input_name)
    if img:
        img.save("card.png")
        with open("card.png", "rb") as f:
            img = File(f)
        await ctx.channel.send(file=img)
    else:
        await ctx.send("Player not found.")

@bot.command()
async def register(ctx, input_name):
    print("hello")
    await ctx.send("hi there")

@bot.command()
async def unregister(ctx, input_name):
    print("hello")
    await ctx.send("hi there")

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

bot.run(getenv("DISCORD_TOKEN"))