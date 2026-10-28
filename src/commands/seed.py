from datetime import datetime, time, timedelta, timezone
import json
import math

from nextcord import Embed, Colour

from rankedutils import rank, constants, db, insight, numb

MATCHES_PER_PAGE = 15
MATCH_TYPES = {1: "Casual", 2: "Ranked", 3: "Private", 4: "Event"}


def get_seed_embed(cursor, seed_info, matches_info):
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
    seed_score = insight.get_seed_score(past_score, past_count, current_score, current_count)

    seed_embed = Embed(
        title=f"Seed Info: `{word_id}`",
        description=(
            f"`{word_id}` has been played in {len(matches_info)} {'matches' if len(matches_info) != 1 else 'match'}."
        ),
        colour=Colour.brand_red()
    )

    seed_score_txt = f"{seed_score:.1%}" if seed_score is not None else "-"
    seed_embed.add_field(
        name=f"Seed score: `{seed_score_txt}`",
        value="",
        inline=True,
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

    completions = [match[4] for match in matches_info if not match[5] and match[3] and match[1] == 2]
    if matches_info:
        played_dates = [match[7] for match in matches_info]
        seed_stats = (
            f"First played: <t:{min(played_dates)}:R>"
            f"\nLast played: <t:{max(played_dates)}:R>"
            f"\nTimes played: `{len(matches_info)}`"
            f"\nCompletions: `{len(completions)}`"
            f"\nAverage completion: `{numb.digital_time(round(sum(completions) / len(completions))) if completions else '-'}`"
            f"\nFastest completion: `{numb.digital_time(min(completions)) if completions else '-'}`"
            f"\n*Note: Completion stats are Ranked-mode only.*"
        )
        seed_embed.add_field(
            name="Seed stats",
            value=seed_stats,
            inline=False,
        )

    return seed_embed


def get_matches_embeds(cursor, matches_info):

    matches_embeds = []
    page_count = math.ceil(len(matches_info) / MATCHES_PER_PAGE)

    if len(matches_info) == 0:
        matches_embeds.append(
            Embed(
                title=f"Match history",
                colour=Colour.brand_red()
            ).set_footer(
                text=constants.FOOTER_TEXT,
                icon_url=constants.FOOTER_ICON,
            ).add_field(name="No matches have ever been played on this seed.", value="", inline=False)
        )

    for i, (match_id, match_type, category, result_uuid, match_time, forfeited, season, date) in enumerate(matches_info):
        if i % MATCHES_PER_PAGE == 0:
            matches_embed = Embed(
                title=f"Match history{' (' + str(i // MATCHES_PER_PAGE + 1) + '/' + str(page_count) + ')' if page_count > 1 else ''}",
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
        name = f"{match_type_txt} Match • S{season} • `{match_id}`"

        if match_type == 3:
            player_names = [
                f"`{nickname}` {'👑' if result_uuid == player_uuid else ''}"
                for nickname, elo, player_uuid
                in runs_info
            ]
            players_line = (
                ", ".join(player_names[:-1])
                + (" and " if len(player_names) > 1 else "")
                + player_names[-1]
            )
        else:
            winner = next((
                nickname
                for nickname, _, player_uuid
                in runs_info
                if player_uuid == result_uuid
            ), None)
            player_tags = [
                f"`{nickname}` "
                + ("🤝" if not winner else "👑" if nickname == winner else "🥀")
                + (f" ({elo})" if elo else "")
                for nickname, elo, _ in runs_info
            ]
            players_line = " vs ".join(player_tags)
        if not result_uuid:
            result_line = f"Drawn at `{numb.digital_time(match_time)}` <t:{date}:R>"
        elif forfeited:
            result_line = f"Forfeited at `{numb.digital_time(match_time)}` <t:{date}:R>"
        else:
            result_line = f"Completed in `{numb.digital_time(match_time)}` <t:{date}:R>"
        url_player = winner if winner else runs_info[0][0]

        value = (
            f"{players_line}"
            f"\n{result_line}"
            f"\n[mcsrranked.com/stats/{url_player}/{match_id}](https://mcsrranked.com/stats/{url_player}/{match_id})"
            "\n"
        )
        matches_embed.add_field(name=name, value=value, inline=False)

    return matches_embeds


def main(seed_info: tuple, cursor):
    matches_info = db.query_db(
        cursor,
        items="id, type, category, result_uuid, time, forfeited, season, date",
        seed_id=seed_info[0],
        order="id DESC"
    ).fetchall()

    seed_embed = get_seed_embed(cursor, seed_info, matches_info)
    matches_embeds = get_matches_embeds(cursor, matches_info)

    return seed_embed, matches_embeds
