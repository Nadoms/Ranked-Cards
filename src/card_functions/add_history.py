from PIL import ImageDraw, ImageFont
import requests

from gen_functions import rank, match, word

def write(card, matches, uuid, response):
    history_font = ImageFont.truetype('minecraft_font.ttf', 26)
    historyed_image = ImageDraw.Draw(card)

    w_d_l_colour = ["#86b8db", "#ee4b2b", "#ffbf00"]

    recent_matches = last_few(matches, 10)
    if not recent_matches:
        historyed_image.text((200, 700), "User has no matches played.", font=history_font, fill="white")
        return card
    
    width = 540
    historyed_image.rectangle([360-width/2, 707, 360+width/2, 775], fill="#122b30", outline="#000000", width=8)
    historyed_image.rectangle([30, 665, 690, 715], fill="#ffffff", outline="#000000", width=8)

    blocks = get_blocks(recent_matches)
    wl = get_wl(recent_matches, uuid)
    for i in range(len(recent_matches)):
        historyed_image.polygon(blocks[i], fill=w_d_l_colour[wl[i]], outline="#122b30", width=3)
        
    description = get_desc(wl, recent_matches, uuid, response)
    full_desc = "".join(description)
    x = 360-word.calc_length(full_desc, 26)/2

    if description[3][0] == "+":
        elo_colour = "#86b8db"
    else:
        elo_colour = "#ee4b2b"
    # desc_colour = ["#ffffff", "#86b8db", "#ffffff", "#ee4b2b", "#ffffff", "#ffbf00", "#ffffff", elo_colour]
    ws_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52fa", "#ffd700"]
    desc_colour = ["#ffffff", ws_colour[min(int(description[1]), 5)], "#ffffff", elo_colour]

    for i in range(len(description)):
        historyed_image.text((x, 723), description[i], font=history_font, fill=desc_colour[i])
        x += word.calc_length(description[i], 26)+26/7
    
    return card

def last_few(matches, desired):
    recent_matches = []
    for match in matches:
        if not match["decayed"]:
            recent_matches.append(match)
        if len(recent_matches) >= desired:
            break
    return recent_matches

def get_blocks(recent_matches):
    blocks = []
    lean_factor = 30
    x1 = 10
    width = 670 / len(recent_matches)
    for i in range(len(recent_matches)):
        x2 = x1 + width
        y1 = 675
        y2 = 705
        placedx1 = max(int(x1), 40)
        placedx2 = min(int(x2), 680)
        leanedx1 = max(int(x1)+lean_factor, 40)
        leanedx2 = min(int(x2)+lean_factor, 680)
        block = [(placedx1, y2), (leanedx1, y1), (leanedx2, y1), (placedx2, y2)]
        blocks.append(block)
        x1 += width
    return blocks

def get_wl(recent_matches, uuid):
    wl = []
    for match in recent_matches:
        if match["result"]["uuid"] == uuid:
            wl.append(0)
        elif match["result"]["uuid"] == None:
            wl.append(2)
        else:
            wl.append(1)
    wl.reverse()
    return wl

def get_desc(wl, recent_matches, uuid, response):
    elo_change = get_elo_change(recent_matches, uuid)
    if elo_change >= 0:
        elo_change = "+" + str(elo_change)
    else:
        elo_change = str(elo_change)

    winstreak = response["statistics"]["season"]["currentWinStreak"]["ranked"]

    description = ["Winstreak: ",  str(winstreak), " / Elo change: ", elo_change] #"W/L/D: ", str(wl.count(0)), "/", str(wl.count(1)), "/", str(wl.count(2)),
    return description

def get_elo_change(recent_matches, uuid):
    elo_change = 0
    for match in recent_matches:
        for player in match["changes"]:
            if player["uuid"] == uuid and player["change"]:
                elo_change += player["change"]
    return elo_change