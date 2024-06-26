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
        return f"Top {round((1-proportion) * 100, 1)}%"
    elif proportion < 0.5:
        return f"Bottom {round(proportion * 100, 1)}%"

def get_raw_time(time):
    raw_time = 0
    time = list(reversed(time.split(":")))

    for i in range(len(time)):
        raw_time += int(time[i]) * (60 ** i)
    
    return raw_time * 1000