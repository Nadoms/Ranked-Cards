from datetime import datetime, timedelta, timezone

from nextcord import Embed, Colour

from rankedutils import constants, db


COUNTRY_MAPPING = {
    "Andorra": "AD",
    "United Arab Emirates": "AE",
    "Afghanistan": "AF",
    "Antigua and Barbuda": "AG",
    "Anguilla": "AI",
    "Albania": "AL",
    "Armenia": "AM",
    "Angola": "AO",
    "Antarctica": "AQ",
    "Argentina": "AR",
    "American Samoa": "AS",
    "Austria": "AT",
    "Australia": "AU",
    "Aruba": "AW",
    "Åland Islands": "AX",
    "Azerbaijan": "AZ",
    "Bosnia and Herzegovina": "BA",
    "Barbados": "BB",
    "Bangladesh": "BD",
    "Belgium": "BE",
    "Burkina Faso": "BF",
    "Bulgaria": "BG",
    "Bahrain": "BH",
    "Burundi": "BI",
    "Benin": "BJ",
    "Saint Barthélemy": "BL",
    "Bermuda": "BM",
    "Brunei Darussalam": "BN",
    "Bolivia": "BO",
    "Bonaire, Sint Eustatius and Saba": "BQ",
    "Brazil": "BR",
    "Bahamas": "BS",
    "Bhutan": "BT",
    "Bouvet Island": "BV",
    "Botswana": "BW",
    "Belarus": "BY",
    "Belize": "BZ",
    "Canada": "CA",
    "Cocos (Keeling) Islands": "CC",
    "Democratic Republic of the Congo": "CD",
    "Central African Republic": "CF",
    "Congo": "CG",
    "Switzerland": "CH",
    "Côte d'Ivoire": "CI",
    "Cook Islands": "CK",
    "Chile": "CL",
    "Cameroon": "CM",
    "China": "CN",
    "Colombia": "CO",
    "Costa Rica": "CR",
    "Cuba": "CU",
    "Cabo Verde": "CV",
    "Curaçao": "CW",
    "Christmas Island": "CX",
    "Cyprus": "CY",
    "Czechia": "CZ",
    "Germany": "DE",
    "Djibouti": "DJ",
    "Denmark": "DK",
    "Dominica": "DM",
    "Dominican Republic": "DO",
    "Algeria": "DZ",
    "Ecuador": "EC",
    "Estonia": "EE",
    "Egypt": "EG",
    "Western Sahara": "EH",
    "Eritrea": "ER",
    "Spain": "ES",
    "Ethiopia": "ET",
    "Finland": "FI",
    "Fiji": "FJ",
    "Falkland Islands": "FK",
    "Micronesia": "FM",
    "Faroe Islands": "FO",
    "France": "FR",
    "Gabon": "GA",
    "United Kingdom": "GB",
    "Grenada": "GD",
    "Georgia": "GE",
    "French Guiana": "GF",
    "Guernsey": "GG",
    "Ghana": "GH",
    "Gibraltar": "GI",
    "Greenland": "GL",
    "Gambia": "GM",
    "Guinea": "GN",
    "Guadeloupe": "GP",
    "Equatorial Guinea": "GQ",
    "Greece": "GR",
    "South Georgia and the South Sandwich Islands": "GS",
    "Guatemala": "GT",
    "Guam": "GU",
    "Guinea-Bissau": "GW",
    "Guyana": "GY",
    "Hong Kong": "HK",
    "Heard and McDonald Islands": "HM",
    "Honduras": "HN",
    "Croatia": "HR",
    "Haiti": "HT",
    "Hungary": "HU",
    "Indonesia": "ID",
    "Ireland": "IE",
    "Israel": "IL",
    "Isle of Man": "IM",
    "India": "IN",
    "British Indian Ocean Territory": "IO",
    "Iraq": "IQ",
    "Iran": "IR",
    "Iceland": "IS",
    "Italy": "IT",
    "Jersey": "JE",
    "Jamaica": "JM",
    "Jordan": "JO",
    "Japan": "JP",
    "Kenya": "KE",
    "Kyrgyzstan": "KG",
    "Cambodia": "KH",
    "Kiribati": "KI",
    "Comoros": "KM",
    "Saint Kitts and Nevis": "KN",
    "North Korea": "KP",
    "South Korea": "KR",
    "Kuwait": "KW",
    "Cayman Islands": "KY",
    "Kazakhstan": "KZ",
    "Lao People's Democratic Republic": "LA",
    "Lebanon": "LB",
    "Saint Lucia": "LC",
    "Liechtenstein": "LI",
    "Sri Lanka": "LK",
    "Liberia": "LR",
    "Lesotho": "LS",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Latvia": "LV",
    "Libya": "LY",
    "Morocco": "MA",
    "Monaco": "MC",
    "Moldova": "MD",
    "Montenegro": "ME",
    "Saint Martin": "MF",
    "Madagascar": "MG",
    "Marshall Islands": "MH",
    "North Macedonia": "MK",
    "Mali": "ML",
    "Myanmar": "MM",
    "Mongolia": "MN",
    "Macao": "MO",
    "Northern Mariana Islands": "MP",
    "Martinique": "MQ",
    "Mauritania": "MR",
    "Montserrat": "MS",
    "Malta": "MT",
    "Mauritius": "MU",
    "Maldives": "MV",
    "Malawi": "MW",
    "Mexico": "MX",
    "Malaysia": "MY",
    "Mozambique": "MZ",
    "Namibia": "NA",
    "New Caledonia": "NC",
    "Niger": "NE",
    "Norfolk Island": "NF",
    "Nigeria": "NG",
    "Nicaragua": "NI",
    "Netherlands": "NL",
    "Norway": "NO",
    "Nepal": "NP",
    "Nauru": "NR",
    "Niue": "NU",
    "New Zealand": "NZ",
    "Oman": "OM",
    "Panama": "PA",
    "Peru": "PE",
    "French Polynesia": "PF",
    "Papua New Guinea": "PG",
    "Philippines": "PH",
    "Pakistan": "PK",
    "Poland": "PL",
    "Saint Pierre and Miquelon": "PM",
    "Pitcairn": "PN",
    "Puerto Rico": "PR",
    "Palestine": "PS",
    "Portugal": "PT",
    "Palau": "PW",
    "Paraguay": "PY",
    "Qatar": "QA",
    "Réunion": "RE",
    "Romania": "RO",
    "Serbia": "RS",
    "Russia": "RU",
    "Rwanda": "RW",
    "Saudi Arabia": "SA",
    "Solomon Islands": "SB",
    "Seychelles": "SC",
    "Sudan": "SD",
    "Sweden": "SE",
    "Singapore": "SG",
    "Saint Helena": "SH",
    "Slovenia": "SI",
    "Svalbard and Jan Mayen": "SJ",
    "Slovakia": "SK",
    "Sierra Leone": "SL",
    "San Marino": "SM",
    "Senegal": "SN",
    "Somalia": "SO",
    "Suriname": "SR",
    "South Sudan": "SS",
    "Sao Tome and Principe": "ST",
    "El Salvador": "SV",
    "Sint Maarten": "SX",
    "Syria": "SY",
    "Eswatini": "SZ",
    "Turks and Caicos Islands": "TC",
    "Chad": "TD",
    "French Southern Territories": "TF",
    "Togo": "TG",
    "Thailand": "TH",
    "Tajikistan": "TJ",
    "Tokelau": "TK",
    "Timor-Leste": "TL",
    "Turkmenistan": "TM",
    "Tunisia": "TN",
    "Tonga": "TO",
    "Turkey": "TR",
    "Trinidad and Tobago": "TT",
    "Tuvalu": "TV",
    "Taiwan": "TW",
    "Tanzania": "TZ",
    "Ukraine": "UA",
    "Uganda": "UG",
    "United States Minor Outlying Islands": "UM",
    "United States of America": "US",
    "Uruguay": "UY",
    "Uzbekistan": "UZ",
    "Holy See": "VA",
    "Saint Vincent and the Grenadines": "VC",
    "Venezuela": "VE",
    "British Virgin Islands": "VG",
    "U.S. Virgin Islands": "VI",
    "Viet Nam": "VN",
    "Vanuatu": "VU",
    "Wallis and Futuna": "WF",
    "Samoa": "WS",
    "Yemen": "YE",
    "Mayotte": "YT",
    "South Africa": "ZA",
    "Zambia": "ZM",
    "Zimbabwe": "ZW",
}


def custom_leaderboard(leaderboard, lb_name, lb_desc, input_name, page):
    embed = Embed(
        title=f"{lb_name} Leaderboard - Page {page + 1}",
        description=f"{lb_desc}\nThere are {len(leaderboard)} players on this leaderboard.\nNote: This is updated nightly.",
        colour=Colour.blurple()
    )

    lb_txt = ""
    start = page * 20
    end = (page + 1) * 20

    conn, cursor = db.start()
    for position, entry in enumerate(leaderboard):
        name = db.get_nick(cursor, entry[3])
        if position < start or position >= end:
            if name.lower() == input_name.lower():
                lb_txt += f" .... | ................ | ..{'.' if lb_name == 'Average Completion' else ''}.. | ......\n"
            else:
                continue
        highlight = ">" if name.lower() == input_name.lower() else " "

        duration = str(timedelta(seconds=entry[0] // 1000))[2:]
        if duration[0] == "0" and lb_name != "Average Completion":
            duration = duration[1:]
        count = f"{entry[2]} c"
        spacing_1 = " " * (3 - len(str(position + 1)))
        spacing_2 = " " * (16 - len(name))
        line = f"{highlight}{spacing_1}#{position + 1} | {name}{spacing_2} | {duration} | {count}\n"
        if position < start:
            lb_txt = line + lb_txt
        else:
            lb_txt += line

    if not lb_txt:
        lb_txt = "Nothing to see here."
    embed.add_field(name="", value=f"```{lb_txt}```", inline=False)

    embed.set_footer(
            text=constants.FOOTER_TEXT,
            icon_url=constants.FOOTER_ICON,
    )
    conn.close()

    return embed


def completion_time_leaderboard(leaderboard, input_name, season, page):
    title = "Completion Time Leaderboard"
    if season:
        title += f" for Season {season}"
    else:
        title = "Lifetime " + title
    title += f" - Page {page + 1}"

    description = "These are the fastest completions."

    embed = Embed(
        title=title, description=description, colour=Colour.blurple()
    )

    lb_txt = ""
    now = datetime.now(timezone.utc)
    start = page * 20
    end = (page + 1) * 20

    for position, entry in enumerate(leaderboard):
        name = entry["user"]["nickname"]
        if position < start or position >= end:
            if name.lower() == input_name.lower():
                lb_txt += f" .... | ................ | .... | ......\n"
            else:
                continue
        highlight = ">" if name.lower() == input_name.lower() else " "

        attribute = str(timedelta(seconds=entry["time"] // 1000))[2:]
        if attribute[0] == "0":
            attribute = attribute[1:]
        then = datetime.fromtimestamp(entry["date"], tz=timezone.utc)
        days = str((now - then).days)
        spacing_0 = " " * (3 - len(days))
        ago = f" | {spacing_0}{days}d ago"
        spacing_1 = " " * (3 - len(str(position + 1)))
        spacing_2 = " " * (16 - len(name))
        line = f"{highlight}{spacing_1}#{position + 1} | {name}{spacing_2} | {attribute}{ago}\n"
        if position < start:
            lb_txt = line + lb_txt
        else:
            lb_txt += line

    if not lb_txt:
        lb_txt = "Nothing to see here."
    embed.add_field(name="", value=f"```{lb_txt}```", inline=False)

    embed.set_footer(
            text=constants.FOOTER_TEXT,
            icon_url=constants.FOOTER_ICON,
    )

    return embed


def elo_leaderboard(leaderboard, input_name, season, country, page):
    title = f"Elo Leaderboard for Season {season}"
    if country:
        title += f" - {country}"
    title += f" - Page {page + 1}"

    ends_at = leaderboard["season"]["endsAt"]
    if ends_at:
        description = f"Season {season} will end <t:{ends_at}:R>."
    else:
        description = f"This is taken from the very end of the season."

    embed = Embed(
        title=title, description=description, colour=Colour.blurple()
    )

    lb_txt = ""
    start = page * 20
    end = (page + 1) * 20

    for position, entry in enumerate(leaderboard["users"]):
        name = entry["nickname"]
        if position < start or position >= end:
            if name.lower() == input_name.lower():
                lb_txt += f" .... | ................ | ....\n"
            else:
                continue
        highlight = ">" if name.lower() == input_name.lower() else " "

        spacing_1 = " " * (3 - len(str(position + 1)))
        spacing_2 = " " * (16 - len(name))
        line = f"{highlight}{spacing_1}#{position + 1} | {name}{spacing_2} | {entry["seasonResult"]["eloRate"]}\n"
        if position < start:
            lb_txt = line + lb_txt
        else:
            lb_txt += line

    if not lb_txt:
        lb_txt = "Nothing to see here."
    embed.add_field(name="", value=f"```{lb_txt}```", inline=False)

    embed.set_footer(
        text=constants.FOOTER_TEXT,
        icon_url=constants.FOOTER_ICON,
    )

    return embed


def phase_points_leaderboard(leaderboard, input_name, season, country, page):
    title = f"Phase Points Leaderboard for Season {season}"
    if country:
        title += f" - {country}"
    title += f" - Page {page + 1}"

    ends_at = leaderboard["phase"]["endsAt"]
    phase = leaderboard["phase"]["number"]
    if ends_at:
        description = f"Phase {phase} will end <t:{ends_at}:R>."
    else:
        description = f"This is taken from the very end of the season."

    embed = Embed(
        title=title, description=description, colour=Colour.blurple()
    )

    lb_txt = ""
    start = page * 20
    end = (page + 1) * 20

    for position, entry in enumerate(leaderboard["users"]):
        name = entry["nickname"]
        if position < start or position >= end:
            if name.lower() == input_name.lower():
                lb_txt += f" .... | ................ | ....\n"
            else:
                continue
        highlight = ">" if name.lower() == input_name.lower() else " "

        spacing_1 = " " * (3 - len(str(position + 1)))
        spacing_2 = " " * (16 - len(name))
        line = f"{highlight}{spacing_1}#{position + 1} | {name}{spacing_2} | {entry["seasonResult"]["phasePoint"]} pts\n"
        if position < start:
            lb_txt = line + lb_txt
        else:
            lb_txt += line

    if not lb_txt:
        lb_txt = "Nothing to see here."
    embed.add_field(name="", value=f"```{lb_txt}```", inline=False)

    embed.set_footer(
        text=constants.FOOTER_TEXT,
        icon_url=constants.FOOTER_ICON,
    )

    return embed
