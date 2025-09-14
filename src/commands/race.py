from datetime import datetime, timedelta, timezone

from nextcord import Embed, Colour


def main(response, input_name):
    id = response["id"]
    title = f"Weekly Race #{id}"
    now = datetime.now(timezone.utc)
    now_int = int(now.timestamp())
    ends_at = response["endsAt"]
    if ends_at > now_int:
        description = f"This weekly race will end <t:{ends_at}:R>."
    else:
        description = f"This weekly race ended <t:{ends_at}:R>."
    leaderboard = response["leaderboard"]

    embed = Embed(
        title=title, description=description, colour=Colour.blurple(), timestamp=now
    )

    value = ""
    found = False

    for run in leaderboard:
        rank = run["rank"]
        name = run["player"]["nickname"]
        if rank > 25:
            if found or not input_name:
                break
            elif name.lower() == input_name.lower():
                value += f" ... | ...             | ...      \n"
            else:
                continue
        if name.lower() == input_name.lower():
            value += ">"
        else:
            value += " "

        time = str(timedelta(milliseconds=run["time"]))[2:11]
        if time[0] == "0":
            time = time[1:]
        spacing_1 = " " * (2 - len(str(rank)))
        spacing_2 = " " * (16 - len(name))
        value += f"{spacing_1}#{rank} | {name}{spacing_2}| {time} \n"

    embed.add_field(name="Leaderboard", value=f"```{value}```", inline=False)

    # embed.set_thumbnail(url=head)
    # embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
    # embed.set_image(url="attachment://ow.png")
    embed.set_footer(
        text="Bot made by @Nadoms",
        icon_url="https://cdn.discordapp.com/avatars/298936021557706754/a_60fb14a1dbfb0d33f3b02cc33579dacf?size=256",
    )

    return embed
