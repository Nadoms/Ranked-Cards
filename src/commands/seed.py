from datetime import datetime, time, timedelta, timezone

from nextcord import Embed, Colour

from rankedutils import rank, constants, db, insight


def main(seed_identifier: str):
    conn, cursor = db.start()

    if seed_identifier.isnumeric():
        (seed_identifier,) = db.query_db(
            cursor,
            items="seed_id",
            id=int(seed_identifier)
        ).fetchone()

    seed_info = db.query_db(
        cursor,
        table="seeds",
        items="id, overworld, bastion, structure_type, structure_contents, triples, singles, small_singles, good_gaps, past_score, past_count, current_score, current_count, word_id",
        where=f"id == {seed_identifier} or word_id == {seed_identifier}"
    ).fetchone()
    (
        seed_id,
        overworld,
        bastion,
        structure_type,
        structure_contents,
        triples,
        singles,
        small_singles,
        good_gaps,
        past_score,
        past_count,
        current_score,
        current_count,
        word_id
    ) = seed_info
    matches_info = db.query_db(
        cursor,
        items="id, type, category, result_uuid, time, forfeited, decayed, season, date",
        seed_id=seed_id,
        order="type, forfeited, time"
    )
    seed_score = insight.get_seed_score(past_score, past_count, current_score, current_count)

    seed_embed = Embed(
        title=f"Seed Info: `{word_id}`",
        description=(
            f"`{word_id}` has been played in {len(matches_info)} matches."
            f"Overworld type: `{overworld.lower().replace('_', ' ').capitalize()}`"
            f"\nBastion type: `{bastion.lower().replace('_', ' ').capitalize()}`"
        ),
        colour=Colour.brand_red()
    )
    seed_embed.add_field(
        name=f"Seed score: `{seed_score * 100}`",
        value="",
        inline=True,
    )
    if overworld != "TREASURE":
        bastion_info = (
            f"Triples: `{triples if triples else 0}`"
            f"\n{'Doubles' if bastion == 'STABLES' else 'Singles'}: `{singles if singles else 0}`"
            f"\n{'Singles' if bastion == 'STABLES' else 'Ruins'}: `{small_singles if small_singles else 0}`"
            f"\nGood gaps: `{good_gaps if good_gaps else 0}`" if bastion == "STABLES" else ""
        ),
        seed_embed.add_field(
            name="Bastion info",
            value=bastion_info,
            inline=True,
        )
    if bastion != "TREASURE":
        bastion_info = (
            f"Triples: `{triples if triples else 0}`"
            f"\n{'Doubles' if bastion == 'STABLES' else 'Singles'}: `{singles if singles else 0}`"
            f"\n{'Singles' if bastion == 'STABLES' else 'Ruins'}: `{small_singles if small_singles else 0}`"
            f"\nGood gaps: `{good_gaps if good_gaps else 0}`" if bastion == "STABLES" else ""
        ),
        seed_embed.add_field(
            name="Bastion info",
            value=bastion_info,
            inline=True,
        )

    for match_id, type, category, result_uuid, time, forfeited, decayed, season, date in matches_info:
        runs_info = db.query_db(
            cursor,
            table="runs",
            items="uuid",
            match_id=match_id
        )
        nick = db.query_db(
            cursor,
            table="players",
            items="nickname",
            uuid=uuid
        ).fetchone()
        name = ""
        value = ""

        player_tags = []
        player_links = []
        for player in sorted(
            match["players"],
            key=lambda x: x["eloRate"] if x["eloRate"] is not None else 0,
            reverse=True
        ):
            player_rank = rank.get_rank(player["eloRate"])
            rank_emote = rank.get_emote(player_rank)
            player_tags.append(
                f"{rank_emote} "
                f"#{player['eloRank']} "
                f"{player['nickname']}"
            )
            player_links.append(
                f"[{player['nickname']}]"
                f"({match['data'][player['uuid']]['liveUrl']})"
            )
        name = " vs ".join(player_tags)
        value = ", ".join(player_links)

        timestamp = int(time() - match["currentTime"] / 1000)
        value += f"\nMatch began <t:{timestamp}:R>."

        embed.add_field(name=name, value=value, inline=False)

    embed.add_field(
        name="Want to show up when you're live?",
        value="Link your twitch to MCSR Ranked in-game.\nTurn the 'Public Stream: Twitch' option on in Ranked settings.",
        inline=False,
    )
    embed.set_footer(
        text=constants.FOOTER_TEXT,
        icon_url=constants.FOOTER_ICON,
    )

    return embed
