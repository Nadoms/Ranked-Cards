import matplotlib as plt
import seaborn as sns
from . import match


def write(card, name, response):
    matches = match.get_recent_matches(response["nickname"])
    sns.displot(matches, x="games ago", kind="kde", bw_adjust=.25)