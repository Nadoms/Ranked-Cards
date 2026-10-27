from datetime import datetime, time, timedelta, timezone
import json
import math

from nextcord import Embed, Colour

from rankedutils import rank, constants, db, insight, numb

MATCHES_PER_PAGE = 15
MATCH_TYPES = {1: "Casual", 2: "Ranked", 3: "Private", 4: "Other"}


def main(seed_info: tuple, cursor):
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
    structure_contents = json.loads(structure_contents)
    matches_info = db.query_db(
        cursor,
        items="id, type, category, result_uuid, time, forfeited, season, date",
        seed_id=seed_id,
        order="id"
    ).fetchall()
    seed_score = insight.get_seed_score(past_score, past_count, current_score, current_count)

    seed_embed = Embed(
        title=f"Seed Info: `{word_id}`",
        description=(
            f"`{word_id}` has been played in {len(matches_info)} matches."
        ),
        colour=Colour.brand_red()
    )
    seed_embed.add_field(
        name=f"Seed score: `{seed_score * 100}`",
        value="",
        inline=True,
    )

    completions = [match[4] for match in matches_info if not match[5] and match[3] and match[1] == 2]

    if matches_info:
        played_dates = [match[7] for match in matches_info]
        seed_history = (
            f"First played: <t:{min(played_dates)}:f>"
            f"\nLast played: <t:{max(played_dates)}:f>"
            f"\nTimes played: `{len(matches_info)}`"
            f"\nCompletions (Ranked): `{len(completions)}`"
        )
        if completions:
            seed_history += (
                f"\nAverage completion (Ranked): `{numb.digital_time(round(sum(completions) / len(completions)))}`"
                f"\nFastest completion (Ranked): `{numb.digital_time(min(completions))}`"
            )
        seed_embed.add_field(
            name="Seed history",
            value=seed_history,
            inline=False,
        )

    item_mapping = {
        "egap": "a notch apple",
        "looting_sword": "a looting sword (!!)",
        "obsidian": "obsidian",
        "golden_carrot": "golden carrots",
        "diamond": "diamonds",
        "carrot": "carrots",
        "completable": "Obsidian-completable",
        "lava": "Lava-completable",
        "full": "Regular ship w/ mast",
        "upsidedown": "Upside down ship",
        "sideways": "Sideways ship",
        "normal": "Regular ship",
    }
    ow_info_list = []
    if structure_type:
        ow_info_list.append(item_mapping[structure_type])
    if structure_contents:
        ow_info_list.append("Contains " + ", ".join(structure_contents[:-1]) + " and " + structure_contents[-1])
    ow_info = "\n".join(ow_info_list)
    seed_embed.add_field(
        name=f"Overworld type: {overworld.lower().replace('_', ' ').capitalize()}",
        value=ow_info,
        inline=True,
    )

    bastion_info = (
        f"Triples: `{triples if triples else 0}`"
        f"\n{'Doubles' if bastion == 'STABLES' else 'Singles'}: `{singles if singles else 0}`"
        f"\n{'Singles' if bastion == 'STABLES' else 'Ruins'}: `{small_singles if small_singles else 0}`"
        f"\nGood gaps: `{good_gaps if good_gaps else 0}`" if bastion == "STABLES" else ""
    ) if bastion != "TREASURE" else ""
    seed_embed.add_field(
        name=f"Bastion type: {bastion.lower().capitalize()}",
        value=bastion_info,
        inline=True,
    )

    matches_embeds = []
    page_count = math.ceil(len(matches_info) / MATCHES_PER_PAGE)

    if len(matches_info) == 0:
        matches_embeds.append(
            Embed(
                title=f"`{word_id}`'s match history",
                colour=Colour.brand_red()
            ).set_footer(
                text=constants.FOOTER_TEXT,
                icon_url=constants.FOOTER_ICON,
            ).add_field(name="No matches have ever been played on this seed.", value="", inline=False)
        )

    for i, (match_id, match_type, category, result_uuid, match_time, forfeited, season, date) in enumerate(matches_info):
        if i % MATCHES_PER_PAGE == 0:
            matches_embed = Embed(
                title=f"`{word_id}`'s match history ({i // MATCHES_PER_PAGE + 1}/{page_count})",
                colour=Colour.brand_red()
            ).set_footer(
                text=constants.FOOTER_TEXT,
                icon_url=constants.FOOTER_ICON,
            )
            matches_embeds.append(matches_embed)

        runs_info = db.query_db(
            cursor,
            table="runs",
            items="players.nickname, runs.eloRate, runs.player_uuid",
            join="players ON players.uuid = runs.player_uuid",
            match_id=match_id
        ).fetchall()

        match_type_txt = MATCH_TYPES[match_type]
        if match_type == 3 and category != "ANY":
            match_type_txt += f" ({category.lower().replace('_', ' ').capitalize()})"
        name = f"Match {match_id} • S{season} • {match_type_txt}"

        if match_type == 3:
            player_names = [f"`{nickname}`" for nickname, elo, player_uuid in runs_info]
            players_line = ", ".join(player_names[:-1]) + " and " + player_names[-1] if len(player_names) > 1 else "".join(player_names)
        else:
            player_tags = [
                f"`{nickname}`" + (f" ({elo})" if elo else "")
                for nickname, elo, player_uuid in runs_info
            ]
            emotes = [
                "🤝" if not result_uuid else "👑" if player_uuid == result_uuid else "🥀"
                for nickname, elo, player_uuid in runs_info
            ]
            players_line = f"{player_tags[0]} {emotes[0]} vs {emotes[1]} {player_tags[1]}"

        if forfeited:
            result_line = f"Forfeited at {numb.digital_time(match_time)}"
        elif result_uuid:
            result_line = f"Completed in {numb.digital_time(match_time)}"
        else:
            result_line = f"Drawn at {numb.digital_time(match_time)}"
        value = f"{players_line}\n{result_line}\n[Match link](https://mcsrranked.com/stats/{match_id})"

        matches_embed.add_field(name=name, value=value, inline=False)

    seed_embed.set_footer(
        text=constants.FOOTER_TEXT,
        icon_url=constants.FOOTER_ICON,
    )

    return seed_embed, matches_embeds
