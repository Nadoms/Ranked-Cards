from PIL import ImageDraw, ImageFont
import requests

from gen_functions import rank, match, word

def write(card, matches, uuid):
    history_font = ImageFont.truetype('minecraft_font.ttf', 20)
    historyed_image = ImageDraw.Draw(card)

    w_d_l_colour = ["#86b8db", "#ee4b2b", "#ffbf00"]

    recent_matches = last_few(matches, 10)
    if not recent_matches:
        historyed_image.text((200, 700), "User has no matches played.", font=history_font, fill="white")
        return card
    
    width = 450
    historyed_image.rectangle([360-width/2, 712, 360+width/2, 765], fill="#122b30", outline="#000000", width=8)
    historyed_image.rectangle([30, 670, 690, 720], fill="#ffffff", outline="#000000", width=8)

    blocks = get_blocks(recent_matches)
    wl = get_wl(recent_matches, uuid)
    for i in range(len(recent_matches)):
        historyed_image.polygon(blocks[i], fill=w_d_l_colour[wl[i]], outline="#122b30", width=3)
        
    description = get_desc(wl, recent_matches, uuid)
    historyed_image.text((360-word.calc_length(description, 20)/2, 725), description, font=history_font, fill="#ffffff")
    
    return card

def last_few(matches, desired):
    recent_matches = []
    for match in matches:
        if not match["is_decay"]:
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
        y1 = 680
        y2 = 710
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
        if match["winner"] == uuid:
            wl.append(0)
        elif match["winner"] == None:
            wl.append(2)
        else:
            wl.append(1)
    wl.reverse()
    return wl

def get_desc(wl, recent_matches, uuid):
    description = ""
    description += f"W/L/D: {wl.count(0)}/{wl.count(1)}/{wl.count(2)}"
    elo_change = get_elo_change(recent_matches, uuid)
    if elo_change >= 0:
        elo_change = "+" + str(elo_change)
    else:
        elo_change = str(elo_change)
    description += f" // Elo change: {elo_change}"
    description += f""
    return description

def get_elo_change(recent_matches, uuid):
    elo_change = 0
    for match in recent_matches:
        for player in match["score_changes"]:
            if player["uuid"] == uuid:
                elo_change += player["change"]
    return elo_change