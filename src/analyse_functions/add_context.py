from gen_functions import match, rank

def write(name, response, match_id):
    insights = {
        "Elo": [1800, 0.1],
        "Final time:": ["10:20", 0.15],
        "End": ["2:00", 0.5],
        "Overworld": ["1:40", 0.22], # pentagon this please...
        "Bastion": ["2:40", 0.18],
        "Fortress": ["1:20", 0.1],
        "Travel": ["2:20", 0.3],
        "Stronghold": ["0:20", 0.05],
        "End": ["2:00", 0.5]
    }
    return insights