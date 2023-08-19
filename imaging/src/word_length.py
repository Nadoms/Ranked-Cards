def calc_length(word, size):
    length = len(word) * 6 - 1
    for letter in word:
        if letter == " ":
            length -= 4
        elif letter == "I":
            length -= 2
        elif letter == "l":
            length -= 3
        elif letter == "i":
            length -= 4
    length *= size / 8
    return length