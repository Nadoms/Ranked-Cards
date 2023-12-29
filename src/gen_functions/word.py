def calc_length(word, size):
    length = len(word) * 6 - 1
    for letter in word:
        if letter in " i.:,":
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
        if letter in " i.:,":
            length -= 4
        elif letter == "l":
            length -= 3
        elif letter in "It":
            length -= 2
    size = round(desired_length / length * 8)
    return size