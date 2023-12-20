from datetime import timedelta
from os import path
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager, FontProperties
import matplotlib.dates as md
import numpy as np
import seaborn as sns
import pandas as pd
from gen_functions import match, rank


def write(uuid, response, type, season):
    matches = match.get_matches(response["nickname"], season)
    columns = ["Games ago", type, "Season"]

    if type == "Elo":
        data = pd.DataFrame(get_elo(uuid, matches, season), columns=columns)
    elif type == "Completion time":
        data = pd.DataFrame(get_comps(uuid, matches, season), columns=columns)
        data["Completion time"] = pd.to_datetime(data["Completion time"], unit='ms')
    
    if len(data) == 0:
        return -1
    
    games_ago = np.array(data['Games ago'])
    metric = np.array(data[type])

    # Get minecraft font.
    fp = "minecraft_font.ttf"
    fontManager.addfont(fp)
    prop = FontProperties(fname=fp)

    # Set parameters.
    custom_params = {'axes.facecolor':'#313338',
                     'axes.edgecolor': '#929589',
                     'figure.facecolor':'#313338',
                     'text.color':'white',
                     'axes.spines.top': False,
                     'axes.grid': True,
                     'grid.color': '#424549',
                     'font.family': prop.get_name()}
    sns.set(font_scale=0.8, rc=custom_params)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    fig.subplots_adjust(top=0.8, left=0.1, right=0.95)
    lineplot = sns.lineplot(data=data, x=data['Games ago'], y=data[type], ax=ax, color='white', alpha=0.8, label=type)

    # Axis adjustments.
    ax.invert_xaxis()
    ax.grid(axis='x')
    if type == "Completion time":
        ax.yaxis.set_major_formatter(md.DateFormatter("%M:%S"))

    # Fill under line.
    if type == "Elo":
        elo_boundaries = [0, 600, 900, 1200, 1500, 2000, 3000]
        for i in range(len(elo_boundaries)):
            if i == len(elo_boundaries) - 1:
                break
            elif i == len(elo_boundaries) - 2:
                colour = "#000000"
            else:
                colour = rank.get_colour(elo_boundaries[i])[0]
            line1 = np.array([elo_boundaries[i]] * len(data))
            line2 = np.clip(metric, 0, elo_boundaries[i+1])
            ax.fill_between(x=games_ago, y1=line2, y2=line1, where=(line2 > line1), color=colour, interpolate=True, alpha=0.3)
    elif type == "Completion time":
        ax.fill_between(x=games_ago, y1=metric, color="#00FFFF", interpolate=True, alpha=0.2)

    # Vertical season lines.
    if season == "Lifetime":
        prev_season = match.get_season()
        for i in range(0, len(data)-1):
            season = data["Season"].loc[data.index[i]]
            if prev_season != season:
                vert = data["Games ago"].loc[data.index[i]]
                ax.axvline(vert, color=[1, 1-0.2*(season-1), 0.1*(season-1)], alpha=0.8, linestyle="--", label=f"Season {season} end", ymin=0.0, ymax=0.5)
            prev_season = season

    # Horizontal best line.
    if type == "Elo":
        horiz = max(data[type])
        label = f"Best elo ({horiz})"
        xpos = 1 - (data[type].idxmax() / (len(data)-1))
    elif type == "Completion time":
        horiz = min(data[type])
        fastest = str(horiz)[-12:-7]
        label = f"Fastest time ({fastest})"
        xpos = 1 - (data[type].idxmin() / (len(data)-1))
    xmin = max(xpos-0.04, 0)
    xmax = min(xpos+0.04, 1)
    ax.axhline(horiz, color="#00FFFF", alpha=0.8, linestyle="--", label=label, xmin=xmin, xmax=xmax)

    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    ax.set_xlim(games_ago[len(data)-1], games_ago[0])
    if type == "Elo":
        ax.set_ylim(min(data[type])-30, max(data[type])+30)
    if type == "Completion time":
        ax.set_ylim(min(data[type])-timedelta(minutes=1), max(data[type])+timedelta(minutes=1))

    file = path.join("src", "graph_functions", "graph.png")

    plt.legend()
    plt.savefig(file)
    return file

def get_elo(uuid, matches, season):
    elo_array = []
    remain = 0
    last_relo = -1

    for game in matches:
        for score_change in game["score_changes"]:
            if score_change["uuid"] != uuid:
                continue

            elo = score_change["score"] + score_change["change"]
            season = game["match_season"]
            if score_change["score"] != -1:
                last_relo = elo
                elo_array.append([remain, elo, season])
            else:
                elo_array.append([remain, last_relo, season])

        remain += 1
    return elo_array

def get_comps(uuid, matches, season):
    comp_array = []
    remain = 0

    for game in matches:
        if game["winner"] != uuid or game["forfeit"] != False:
            continue

        comp = game["final_time"]
        season = game["match_season"]
        comp_array.append([remain, comp, season])

        remain += 1
    return comp_array