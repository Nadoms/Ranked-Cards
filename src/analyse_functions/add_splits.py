from os import path
from PIL import ImageDraw, Image

def write(analysis, uuids, response, match_id):
    splitted_image = ImageDraw.Draw(analysis)
    x_values = [710, 1210]

    final_time = response["final_time"]
    splits = extract_splits(uuids, response, final_time)
    split_colours = ["#afacf9", "#b43234", "#2b2937", "#600000", "#3f5cf9", "#818181", "#e4e7a9"]
    textures = ["overworld", "nether", "bastion", "fortress", "blind", "stronghold", "end"]

    for i in range(0, 2):
        x = x_values[i]
        splitted_image.rectangle([x-25, 250-5, x+25, 1100+5], fill="#000000", outline="#ffffff", width=2)

    for i in range(0, 2):
        x = x_values[i]

        prog_coords, progressions, event_coords, events = process_advancements(splits[i], final_time)
        
        for i in range(len(progressions)):
            y1 = prog_coords[i]
            if i >= len(progressions) - 1:
                y2 = 1100
            else:
                y2 = prog_coords[i+1]
            
            file = path.join("src", "pics", "textures", "cleantextures", f"{textures[i]}.png")
            texture = Image.open(file).resize(analysis.size)

            mask = Image.new("L", analysis.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rectangle([x-20, y1, x+20, y2], fill="#ffffff", outline="#000000", width=2)
            analysis = Image.composite(texture, analysis, mask)

    return analysis

def process_advancements(splits, final_time):
    y = 250
    length = 850

    prog_coords = [y]
    progressions = [0]
    event_coords = [y]
    events = []
    
    for advancement in splits:
        prog_coord = None
        event_coord = None

        if advancement == "story.enter_the_nether":
            prog_coord = splits[advancement]
            progressions.append(1)

        elif advancement == "nether.find_bastion":
            prog_coord = splits[advancement]
            progressions.append(2)

        elif advancement == "nether.obtain_blaze_rod":
            prog_coord = splits[advancement]
            progressions.append(3)

        elif advancement == "projectelo.timeline.blind_travel":
            prog_coord = splits[advancement]
            progressions.append(4)

        elif advancement == "story.follow_ender_eye":
            prog_coord = splits[advancement]
            progressions.append(5)

        elif advancement == "story.enter_the_end":
            prog_coord = splits[advancement]
            progressions.append(6)

        elif advancement == "nether.find_fortress":
            event_coord = splits[advancement]
            events.append(1)

        elif advancement == "projectelo.timeline.reset":
            event_coord = splits[advancement]
            events.append(2)

        elif advancement == "projectelo.timeline.death":
            event_coord = splits[advancement]
            events.append(3)

        elif advancement == "lose":
            event_coord = splits[advancement]
            events.append(4)

        elif advancement == "finish":
            event_coord = splits[advancement]
            events.append(5)

        elif advancement == "forfeit":
            event_coord = splits[advancement]
            events.append(6)

        elif advancement == "win":
            event_coord = splits[advancement]
            events.append(7)

        if prog_coord:
            prog_coord = y + length * splits[advancement] / final_time
            prog_coords.append(prog_coord)
        elif event_coord:
            event_coord = y + length * splits[advancement] / final_time
            event_coords.append(event_coord)

        print("did", advancement, "in", splits[advancement] / 1000 / 60, "minutes.")

    return [prog_coords, progressions, event_coords, events]


def extract_splits(uuids, response, final_time):
    timelines = response["timelines"]
    timelines.reverse()
    player_0 = {}
    player_1 = {}

    for time in timelines:
        if time["uuid"] == uuids[0]:
            player_0[time["timeline"]] = time["time"]
        elif time["uuid"] == uuids[1]:
            player_1[time["timeline"]] = time["time"]
    
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
            outcome_0 = "finish"
            outcome_1 = "lose"

    player_0[outcome_0] = final_time
    player_1[outcome_1] = final_time
    
    return [player_0, player_1]