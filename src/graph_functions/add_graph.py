from os import path
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from gen_functions import match, rank


def write(name, uuid, response, type):
    matches = match.get_recent_matches(response["nickname"])
    data = pd.DataFrame(get_elo(uuid, matches), columns=["Games ago", "Elo"])
    
    games_ago = np.array(data['Games ago'])
    elo = np.array(data['Elo'])

    custom_params = {'axes.facecolor':'#313338',
                     'axes.edgecolor': '#929589',
                     'figure.facecolor':'#313338',
                     'text.color':'white',
                     'axes.spines.top': False,
                     'axes.grid': True,
                     'grid.color': '#424549'}
    sns.set(style="dark", rc=custom_params)

    fig, ax = plt.subplots(figsize=(8, 5))
    lineplot = sns.lineplot(data=data, x=games_ago, y=elo, ax=ax, color='white', alpha=0.8)

    ax.invert_xaxis()
    ax.grid(axis='x')

    elo_boundaries = [0, 600, 900, 1200, 1500, 2000, 3000]
    for i in range(len(elo_boundaries)):
        if i == len(elo_boundaries) - 1:
            break
        colour = rank.get_colour(elo_boundaries[i])[0]
        line1 = np.array([elo_boundaries[i]] * len(data))
        line2 = np.clip(elo, 0, elo_boundaries[i+1])
        ax.fill_between(x=games_ago, y1=line2, y2=line1, where=(line2 > line1) , color=colour, interpolate=True, alpha=0.2)

    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    ax.set_xlim(games_ago[len(data)-1], games_ago[0])
    ax.set_ylim(min(data['Elo'])-30, max(data['Elo'])+30)

    file = path.join("src", "graph_functions", "graph.png")
    plt.savefig(file)
    return file

def get_elo(uuid, matches):
    elo_array = []
    remain = 0
    for match in matches:
        for score_change in match["score_changes"]:
            if score_change["uuid"] == uuid:
                elo = score_change["score"] + score_change["change"]
                elo_array.append([remain, elo])
        remain += 1
    return elo_array