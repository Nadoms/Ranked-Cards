def get_rank(elo):
    if elo < 0:
        return -1
    elif elo < 600:
        return 0
    elif elo < 900:
        return 1
    elif elo < 1200:
        return 2
    elif elo < 1500:
        return 3
    elif elo < 2000:
        return 4
    elif elo >= 2000:
        return 5
    else:
        return -1

def get_colour(elo):
    if elo < 600:
        return ["#151716", "#ffffff"]
    elif elo < 900:
        return ["#bdbdbd", "#bdbdbd"]
    elif elo < 1200:
        return ["#fad43d", "#fad43d"]
    elif elo < 1500:
        return ["#12b14e", "#12b14e"]
    elif elo < 2000:
        return ["#5ac9c0", "#5ac9c0"]
    elif elo >= 2000:
        return ["#3e3a3e", "#fad43d"]
    else:
        return 0