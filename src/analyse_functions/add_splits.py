from datetime import timedelta
from os import path
from PIL import ImageDraw, Image, ImageFont

from gen_functions import word

# 1. label splits with times
# 2 add events
# 3 analyse

def write(analysis, uuids, response, match_id):
    splitted_image = ImageDraw.Draw(analysis)
    x_values = [550, 1370]

    final_time = response["final_time"]
    splits = extract_splits(uuids, response, final_time)
    split_colours = ["#afacf9", "#b43234", "#2b2937", "#600000", "#3f5cf9", "#818181", "#e4e7a9"]
    textures = ["overworld", "nether", "bastion", "fortress", "blind", "stronghold", "end"]
    advancements = []

    for i in range(0, 2):
        x = x_values[i]
        advancements.append(process_advancements(splits[i], final_time))
        splitted_image.rectangle([x-33, 250-8, x+33, 1100+8], fill="#000000", outline="#ffffff", width=4)

    for i in range(0, 2):
        x = x_values[i]
        prog_coords = advancements[i][0]
        progressions = advancements[i][1]
        
        for j in range(len(progressions)):
            y1 = prog_coords[j]
            if j >= len(progressions) - 1:
                y2 = 1100
            else:
                y2 = prog_coords[j+1]
                
            file = path.join("src", "pics", "textures", "cleantextures", f"{textures[progressions[j]]}.jpg")
            texture = Image.open(file)

            mask = Image.new("L", analysis.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rectangle([x-25, y1, x+25, y2], fill="#ffffff", outline="#000000", width=2)
            analysis = Image.composite(texture, analysis, mask)
    
    for i in range(0, 2):
        event_coords = advancements[i][3]
        events = advancements[i][4]
        side = 1 - 2*i

        for j in range(len(events)):
            if j > 9:
                continue

            icon = get_event_icon(events[j])

            side *= -1

            x = x_values[i] + side * 80 - int(icon.size[0]/2)
            y = event_coords[j] - int(icon.size[1]/2)

            analysis.paste(icon, (x, y), icon)

            # line = [(x-50, y), (x+50, y)]
            # evented_image.line(line, fill="#ffff00", width=3)
            # evented_image.text((x, y), "", fill="#ffff00")
    splitted_image = ImageDraw.Draw(analysis)

    for i in range(0, 2):
        coords = advancements[i][3]
        times = advancements[i][5]
        side = 1 - 2*i

        for j in range(len(coords)):
            time = str(timedelta(milliseconds=times[j]))[2:7].lstrip("0")
            time_size = 25
            time_font = ImageFont.truetype('minecraft_font.ttf', time_size)

            if j == 0:
                time = "START!"

            side *= -1

            x = x_values[i] + side * 130 + (side-1) * word.calc_length(time, time_size) / 2
            y = coords[j] - word.horiz_to_vert(time_size) / 2
            
            splitted_image.text((x, y), time, font=time_font, fill="#44ffff")

    return analysis

def get_event_icon(event):
    file = path.join("src", "pics", "items", f"{event}.webp")
    icon = Image.open(file)
    icon = icon.resize((round(icon.size[0]*0.4), round(icon.size[1]*0.4)))
    return icon

def process_advancements(splits, final_time):
    y = 250
    length = 850
    prog_coords = [y]
    progressions = [0]
    prog_times = [0]
    event_coords = [y]
    events = [0]
    event_times = [0]
    
    for advancement in splits:
        prog_time = None
        event_time = None

        if advancement["timeline"] == "projectelo.timeline.reset":
            prog_time = advancement["time"]
            progressions.append(0)
            event_time = advancement["time"]
            events.append(0)

        elif advancement["timeline"] == "story.enter_the_nether":
            prog_time = advancement["time"]
            progressions.append(1)
            event_time = advancement["time"]
            events.append(1)

        elif advancement["timeline"] == "nether.find_bastion":
            prog_time = advancement["time"]
            progressions.append(2)
            event_time = advancement["time"]
            events.append(2)

        elif advancement["timeline"] == "nether.find_fortress":
            prog_time = advancement["time"]
            progressions.append(3)

        elif advancement["timeline"] == "nether.obtain_blaze_rod":
            prog_time = advancement["time"]
            progressions.append(3)
            event_time = advancement["time"]
            events.append(3)

        elif advancement["timeline"] == "projectelo.timeline.blind_travel":
            prog_time = advancement["time"]
            progressions.append(4)
            event_time = advancement["time"]
            events.append(4)

        elif advancement["timeline"] == "story.follow_ender_eye":
            prog_time = advancement["time"]
            progressions.append(5)
            event_time = advancement["time"]
            events.append(5)

        elif advancement["timeline"] == "story.enter_the_end":
            prog_time = advancement["time"]
            progressions.append(6)
            event_time = advancement["time"]
            events.append(6)

        elif advancement["timeline"] == "projectelo.timeline.death":
            event_time = advancement["time"]
            events.append(7)

        elif advancement["timeline"] == "win":
            event_time = advancement["time"]
            events.append(8)

        elif advancement["timeline"] == "finish":
            event_time = advancement["time"]
            events.append(9)

        elif advancement["timeline"] == "lose":
            event_time = advancement["time"]
            events.append(10)

        elif advancement["timeline"] == "forfeit":
            event_time = advancement["time"]
            events.append(11)

        if prog_time:
            prog_coord = int(y + length * prog_time / final_time)
            prog_coords.append(prog_coord)
            prog_times.append(prog_time)
        if event_time:
            event_coord = int(y + length * event_time / final_time)
            event_coords.append(event_coord)
            event_times.append(event_time)

    return [prog_coords, progressions, prog_times, event_coords, events, event_times]


def extract_splits(uuids, response, final_time):
    timelines = response["timelines"]
    timelines.reverse()
    player_0 = []
    player_1 = []

    for time in timelines:
        if time["uuid"] == uuids[0]:
            player_0.append({"timeline": time["timeline"], "time": time["time"]})
        elif time["uuid"] == uuids[1]:
            player_1.append({"timeline": time["timeline"], "time": time["time"]})
    
    if response["forfeit"] == True:
        if response["winner"] == uuids[0]:
            outcome_0 = "win"
            outcome_1 = "forfeit"
        elif response["winner"] == uuids[1]:
            outcome_0 = "forfeit"
            outcome_1 = "win"
        elif response["winner"] == None:
            outcome_0 = "draw"
            outcome_1 = "draw"
    else:
        if response["winner"] == uuids[0]:
            outcome_0 = "finish"
            outcome_1 = "lose"
        elif response["winner"] == uuids[1]:
            outcome_0 = "lose"
            outcome_1 = "finish"

    player_0.append({"timeline": outcome_0, "time": final_time})
    player_1.append({"timeline": outcome_1, "time": final_time})
    
    return [player_0, player_1]