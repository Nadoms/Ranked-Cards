from datetime import datetime, timedelta, timezone
import re

from nextcord import Embed, Colour

from rankedutils import constants, db, numb


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


class LBEmbeds():

    def __init__(self, max_page, title, description, header):
        self.max_page = max_page
        self.title = title
        self.description = description
        self.header = header
        temp = header.replace(" | ", "/")[1:]
        temp = re.sub(r"(\w|\s)", ".", temp)
        self.separator = " " + temp
        self.embeds = []

    def construct_lb(self, lb_rows, user_rank = None, user_row = None):
        self.embeds = []
        for page in range(self.max_page):
            page_title = f"{self.title} ({page + 1}/{self.max_page})"

            embed = Embed(
                title=page_title, description=self.description, colour=Colour.blurple()
            ).set_footer(
                text=constants.FOOTER_TEXT,
                icon_url=constants.FOOTER_ICON,
            )

            start = page * 20
            end = (page + 1) * 20

            page_rows = lb_rows[start:end]
            if not page_rows:
                value = "Nothing to see here."
            else:
                page_rows = [self.header] + page_rows
                if user_rank is not None:
                    if user_rank < start:
                        page_rows.insert(1, user_row)
                        page_rows.insert(2, self.separator)
                    elif user_rank >= end:
                        page_rows.append(self.separator)
                        page_rows.append(user_row)
                value = "```" + "\n".join(page_rows) + "```"
            embed.add_field(name="", value=value, inline=False)
            self.embeds.append(embed)

        return self.embeds


class CustomLBEmbeds(LBEmbeds):

    def __init__(self, max_page, lb_name, description, lb_type):
        self.is_time = lb_type in ("avg", "split", "bastion", "ow")
        self.is_ratio = lb_type in ("winrate", "ffl", "trwr")
        self.needs_samples = self.is_time or self.is_ratio
        header_value = "time " if self.is_time else f"{lb_type} "
        header_samples = " (samples)" if self.needs_samples else ""
        header = f" rank  | username         | {header_value}{header_samples}"
        description = f"{description}\nThis leaderboard is updated nightly."
        title = f"{lb_name} Leaderboard"
        self.lb_name = lb_name
        super().__init__(max_page, title, description, header)

    def extract_lb(self, leaderboard, input_name):
        conn, cursor = db.start()

        user_row = None
        user_rank = None
        lb_rows = []

        for position, entry in enumerate(leaderboard):
            name = db.get_nick(cursor, entry[2])
            if self.is_time:
                value = numb.digital_time(entry[0])
            elif self.is_ratio:
                value = f"{round(entry[0] * 100, 1)}%"
            else:
                value = entry[0]
            highlight = ">" if name.lower() == input_name.lower() else " "
            samples = f" ({entry[3]})" if self.needs_samples else ""
            lb_row = (
                f"{highlight}{'#' + str(position + 1):>5} | "
                f"{name:<16} | {value:>5}{samples}"
            )

            if name.lower() == input_name.lower():
                user_row = lb_row
                user_rank = position
            lb_rows.append(lb_row)

        conn.close()
        return self.construct_lb(lb_rows, user_rank, user_row)


class CompletionTimeLBEmbeds(LBEmbeds):

    def __init__(self, max_page, season):
        title = "Completion Time Leaderboard"
        if season:
            title += f" in Season {season}"
        else:
            title = "Lifetime " + title
        header = " rank  | username         | time  (age)"
        description = "These are the fastest completions."
        super().__init__(max_page, title, description, header)

    def extract_lb(self, leaderboard, input_name):
        now = datetime.now(timezone.utc)

        user_row = None
        user_rank = None
        lb_rows = []

        for position, entry in enumerate(leaderboard):
            name = entry["user"]["nickname"]
            duration = numb.digital_time(entry["time"])
            days = (now - datetime.fromtimestamp(
                entry["date"],
                tz=timezone.utc
            )).days
            highlight = ">" if name.lower() == input_name.lower() else " "
            lb_row = (
                f"{highlight}{'#' + str(position + 1):>5} | "
                f"{name:<16} | {duration} ({days:>3}d ago)"
            )

            if name.lower() == input_name.lower():
                user_row = lb_row
                user_rank = position
            lb_rows.append(lb_row)

        return self.construct_lb(lb_rows, user_rank, user_row)


class EloLBEmbeds(LBEmbeds):

    def __init__(self, max_page, season, country = None):
        self.season = season
        title = f"Elo Leaderboard in Season {season}"
        if country:
            title += f" - {country}"
        header = " rank  | username         | elo "
        description = "This is taken from the very end of the season."
        super().__init__(max_page, title, description, header)

    def extract_lb(self, leaderboard, input_name):
        ends_at = leaderboard["season"]["endsAt"]
        if ends_at:
            self.description = f"Season {self.season} will end <t:{ends_at}:R>."

        user_row = None
        user_rank = None
        lb_rows = []

        for position, entry in enumerate(leaderboard["users"]):
            name = entry["nickname"]
            highlight = ">" if name.lower() == input_name.lower() else " "
            lb_row = (
                f"{highlight}{'#' + str(position + 1):>5} | "
                f"{name:<16} | {entry["seasonResult"]["eloRate"]}"
            )

            if name.lower() == input_name.lower():
                user_row = lb_row
                user_rank = position
            lb_rows.append(lb_row)

        return self.construct_lb(lb_rows, user_rank, user_row)


class PhasePointsLBEmbeds(LBEmbeds):

    def __init__(self, max_page, season, country=None):
        title = f"Phase Points Leaderboard in Season {season}"
        if country:
            title += f" - {country}"
        header = " rank  | username         | pts "
        description = "This is taken from the very end of the season."
        super().__init__(max_page, title, description, header)

    def extract_lb(self, leaderboard, input_name):
        ends_at = leaderboard["phase"]["endsAt"]
        phase = leaderboard["phase"]["number"]
        if ends_at:
            self.description = f"Phase {phase} will end <t:{ends_at}:R>."

        user_row = None
        user_rank = None
        lb_rows = []

        for position, entry in enumerate(leaderboard["users"]):
            name = entry["nickname"]
            highlight = ">" if name.lower() == input_name.lower() else " "
            lb_row = (
                f"{highlight}{'#' + str(position + 1):>5} | "
                f"{name:<16} | {entry['seasonResult']['phasePoint']} pts"
            )

            if name.lower() == input_name.lower():
                user_row = lb_row
                user_rank = position
            lb_rows.append(lb_row)

        return self.construct_lb(lb_rows, user_rank, user_row)
