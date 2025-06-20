from datetime import datetime
import math
import gen_functions.numb as numb


def calc_length(word, size):
    length = len(word) * 6 - 1
    for letter in word:
        if letter == " ":
            length -= 4
        elif letter in " i.:,!":
            length -= 4
        elif letter == "l":
            length -= 3
        elif letter in "It":
            length -= 2
        elif letter == "@":
            length += 1
    length *= size / 8
    return round(length)


def calc_size(word, desired_length):
    length = len(word) * 6 - 1
    for letter in word:
        if letter == " ":
            length -= 5
        elif letter in " i.:,!":
            length -= 4
        elif letter == "l":
            length -= 3
        elif letter in "It":
            length -= 2
        elif letter == "@":
            length += 1
    size = round(desired_length / length * 8)
    return size


def horiz_to_vert(size):
    size = round(size * 7 / 5)
    return size


def percentify(proportion):
    if proportion >= 0.5:
        return f"Top {numb.round_sf((1-proportion) * 100, 2)}%"
    return f"Bottom {numb.round_sf(proportion * 100, 2)}%"


def get_raw_time(time):
    raw_time = 0
    time = list(reversed(time.split(":")))

    for i, value in enumerate(time):
        raw_time += int(value) * (60**i)

    return raw_time * 1000


def get_date(timestamp):
    date = datetime.fromtimestamp(timestamp)
    delta_date = datetime.now() - date
    date_str = f"Played {date.strftime('%d.%m.%y')} - "
    date_str += get_ago(timestamp)
    return date_str


def get_ago(timestamp):
    date = datetime.fromtimestamp(timestamp)
    delta_date = datetime.now() - date
    if delta_date.days >= 1:
        return f"{delta_date.days}d ago"
    elif delta_date.total_seconds() / 3600 >= 1:
        return f"{math.floor(delta_date.total_seconds() / 3600)}h ago"
    else:
        return f"{math.floor(delta_date.total_seconds() / 60)}m ago"


def process_split(then, process):
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{process} took {diff}ms")
    return now
