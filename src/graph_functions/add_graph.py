from datetime import timedelta
import math
from os import path
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager, FontProperties
import matplotlib.dates as md
import numpy as np
import seaborn as sns
import pandas as pd

from gen_functions import games, rank


def write(uuid, matches, data_type, season):
    columns = ["Games ago", data_type, data_type + " (smoothed)", "Season"]

    if len(matches) <= 1:
        return -1

    if data_type == "Elo":
        elos = get_smoothed_data(get_elo(uuid, matches, season))
        data = pd.DataFrame(elos, columns=columns)
    elif data_type == "Completion time":
        comps = get_comps(uuid, matches, season)
        if len(comps) <= 1:
            return -1
        comps = get_smoothed_data(comps)
        data = pd.DataFrame(comps, columns=columns)
        data["Completion time"] = pd.to_datetime(data["Completion time"], unit='ms')
        data["Completion time (smoothed)"] = pd.to_datetime(data["Completion time (smoothed)"], unit='ms')

    games_ago = np.array(data['Games ago'])
    metric = np.array(data[data_type])

    # smoothed_metric = np.array(data[data_type + " (smoothed)"])
    # xy_spline = make_interp_spline(games_ago, smoothed_metric)
    # x_ = np.linspace(games_ago.min(), games_ago.max(), 500)
    # y_ = xy_spline(x_)

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
    sns.lineplot(data=data, x=data['Games ago'], y=data[data_type], ax=ax, color='white', alpha=0.7, label=data_type)
    sns.lineplot(data=data, x=data['Games ago'], y=data[data_type + " (smoothed)"], ax=ax, color='#FFFF00', alpha=1)

    # Axis adjustments.
    ax.invert_xaxis()
    ax.grid(axis='x')
    if data_type == "Completion time":
        ax.yaxis.set_major_formatter(md.DateFormatter("%M:%S"))

    # Fill under line.
    if data_type == "Elo":
        elo_boundaries = [0, 600, 900, 1200, 1500, 2000, 3000]
        for i, elo_boundary in enumerate(elo_boundaries):
            if i == len(elo_boundaries) - 1:
                break
            if i == len(elo_boundaries) - 2:
                colour = "#000000"
            else:
                colour = rank.get_colour(elo_boundary)[0]
            line1 = np.array([elo_boundary] * len(data))
            line2 = np.clip(metric, 0, elo_boundaries[i+1])
            ax.fill_between(x=games_ago, y1=line2, y2=line1, where=(line2 > line1), color=colour, interpolate=True, alpha=0.3)
    elif data_type == "Completion time":
        ax.fill_between(x=games_ago, y1=metric, color="#00FFFF", interpolate=True, alpha=0.2)

    # Vertical season lines.
    if season == "Lifetime":
        prev_season = games.get_season()
        for i in range(0, len(data)-1):
            season = data["Season"].loc[data.index[i]]
            if prev_season != season:
                vert = data["Games ago"].loc[data.index[i]]
                ax.axvline(vert, color=[1, 1-0.2*(season-1), 0.1*(season-1)], alpha=0.8, linestyle="--", label=f"Season {season} end", ymin=0.0, ymax=0.5)
            prev_season = season

    # Horizontal best line.
    if data_type == "Elo":
        horiz = max(data[data_type])
        label = f"Best elo ({horiz})"
        xpos = 1 - (data[data_type].idxmax() / (len(data)-1))
    elif data_type == "Completion time":
        horiz = min(data[data_type])
        fastest = str(horiz)[-12:-7]
        label = f"Fastest time ({fastest})"
        xpos = 1 - (data[data_type].idxmin() / (len(data)-1))
    xmin = max(xpos-0.04, 0)
    xmax = min(xpos+0.04, 1)
    ax.axhline(horiz, color="#00FFFF", alpha=0.8, linestyle="--", label=label, xmin=xmin, xmax=xmax)

    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    ax.set_xlim(games_ago[len(data)-1], games_ago[0])
    if data_type == "Elo":
        ax.set_ylim(min(data[data_type])-30, max(data[data_type])+30)
    if data_type == "Completion time":
        ax.set_ylim(min(data[data_type])-timedelta(minutes=1), max(data[data_type])+timedelta(minutes=1))

    file = path.join("src", "graph_functions", "graph.png")

    plt.legend()
    plt.savefig(file)
    return file

def get_elo(uuid, matches, season):
    elo_array = []
    remain = 0
    last_relo = -1

    for game in matches:
        for score_change in game["changes"]:
            if score_change["uuid"] != uuid:
                continue

            if score_change["change"] != None:
                elo = score_change["eloRate"] + score_change["change"]
            season = game["season"]

            if score_change["eloRate"]:
                last_relo = elo
                elo_array.append([remain, elo, season])
            else:
                elo_array.append([remain, last_relo, season])

        remain += 1
    return elo_array

def get_comps(uuid, matches, season):
    comp_array = []
    remain = 0

    for match in matches:
        if match["decayed"] or match["result"]["uuid"] != uuid or match["forfeited"] != False:
            continue

        comp = match["result"]["time"]
        season = match["season"]
        comp_array.append([remain, comp, season])

        remain += 1
    return comp_array

def get_smoothed_data(data_array, smoothing=-1):
    if smoothing == -1:
        smoothing = math.ceil(len(data_array) / 10)
    running_total = 0
    smoothed_array = []
    length = len(data_array)
    count = smoothing+1

    for i in range(count):
        running_total += data_array[i][1]

    for i in range(length):
        smoothed_array.append([data_array[i][0], data_array[i][1], running_total / count, data_array[i][2]])
        if i+smoothing < length-1:
            running_total += data_array[i+smoothing+1][1]
            count += 1
        if i-smoothing >= 0:
            running_total -= data_array[i-smoothing][1]
            count -= 1

    return smoothed_array
