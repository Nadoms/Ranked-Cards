def calc_length(word, size):
    length = len(word) * 6 - 1
    for letter in word:
        if letter in " i.:":
            length -= 4
        elif letter == "l":
            length -= 3
        elif letter in "It":
            length -= 2
    length *= size / 8
    return round(length)