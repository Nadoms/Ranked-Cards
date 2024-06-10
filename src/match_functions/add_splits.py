from datetime import timedelta
from os import path
from PIL import ImageDraw, Image, ImageFont

from gen_functions import word

def write(chart, uuids, response):
    splitted_image = ImageDraw.Draw(chart)
    middle = 600
    x_values = [middle-70, middle+70]
    y_values = [550, 1800]
    x_padding = 50
    y_padding = 8

    final_time = response["result"]["time"]
    splits = extract_splits(uuids, response, final_time)
    textures = ["overworld", "nether", "bastion", "fortress", "blind", "stronghold", "end"]
    advancements = []

    for i in range(0, 2):
        rect_coords = [x_values[i]-x_padding, y_values[0]-y_padding, x_values[i]+x_padding, y_values[1]+y_padding]
        advancements.append(process_advancements(splits[i], final_time))
        splitted_image.rectangle(rect_coords, fill="#000000", outline="#ffffff", width=4)

    for i in range(0, 2):
        x = x_values[i]
        prog_coords = advancements[i][0]
        progressions = advancements[i][1]
        
        for j in range(len(progressions)):
            y1 = prog_coords[j]
            if j >= len(progressions) - 1:
                y2 = 1800
            else:
                y2 = prog_coords[j+1]
                
            file = path.join("src", "pics", "textures", "cleantextures", f"{textures[progressions[j]]}.jpg")
            texture = Image.open(file)

            mask = Image.new("L", chart.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rectangle([x-42, y1+3, x+42, y2-3], fill="#ffffff", outline="#000000", width=2)
            chart = Image.composite(texture, chart, mask)

            outlined_image = ImageDraw.Draw(chart)
            outlined_image.rectangle([x-42, y1+3, x+42, y2-3], outline="#ffffff", width=2)

    
    for i in range(0, 2):
        event_coords = advancements[i][3]
        events = advancements[i][4]
        is_shifted = False

        for j in range(len(events)):
            icon = get_event_icon(events[j])

            x = x_values[i] + (2*i-1) * 105 - int(icon.size[0]/2)
            y = event_coords[j] - int(icon.size[1]/2)

            if 0 <= event_coords[j] - event_coords[j-1] <= 40 and not is_shifted:
                x += (2*i-1) * 220
                is_shifted = True
            else:
                is_shifted = False

            chart.paste(icon, (x, y), icon)

    splitted_image = ImageDraw.Draw(chart)

    for i in range(0, 2):
        coords = advancements[i][3]
        times = advancements[i][5]
        is_shifted = False

        for j in range(len(coords)):
            time = str(timedelta(milliseconds=times[j]))[2:7].lstrip("0")
            if time[0] == ":":
                time = "0" + time
            time_size = 35
            time_font = ImageFont.truetype('minecraft_font.ttf', time_size)

            if j == 0:
                time = "START!"

            x = x_values[i] + (2*i-1) * 160 + (i-1) * word.calc_length(time, time_size)
            y = coords[j] - word.horiz_to_vert(time_size) / 2

            if 0 <= coords[j] - coords[j-1] <= 40 and not is_shifted:
                x += (2*i-1) * 220
                is_shifted = True
            else:
                is_shifted = False
            
            splitted_image.text((x, y), time, font=time_font, fill="#44ffff")

    return chart

def get_event_icon(event):
    file = path.join("src", "pics", "items", f"{event}.webp")
    icon = Image.open(file)
    icon = icon.resize((80, 80))
    return icon

def process_advancements(splits, final_time):
    y = 550
    length = 1800 - y
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

    for event in timelines:
        if event["uuid"] == uuids[0]:
            player_0.append({"timeline": event["type"], "time": event["time"]})
        elif event["uuid"] == uuids[1]:
            player_1.append({"timeline": event["type"], "time": event["time"]})
    
    if response["forfeited"] == True:
        if response["result"]["uuid"] == uuids[0]:
            outcome_0 = "win"
            outcome_1 = "forfeit"
        elif response["result"]["uuid"] == uuids[1]:
            outcome_0 = "forfeit"
            outcome_1 = "win"
        elif response["result"]["uuid"] == None:
            outcome_0 = "draw"
            outcome_1 = "draw"
    else:
        if response["result"]["uuid"] == uuids[0]:
            outcome_0 = "finish"
            outcome_1 = "lose"
        elif response["result"]["uuid"] == uuids[1]:
            outcome_0 = "lose"
            outcome_1 = "finish"

    player_0.append({"timeline": outcome_0, "time": final_time})
    player_1.append({"timeline": outcome_1, "time": final_time})
    
    return [player_0, player_1]