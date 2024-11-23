from datetime import timedelta
from math import log10, floor


def round_sf(num, sf):
    if num == 0:
        return num

    round_amt = -int(floor(log10(abs(num)))) - 1 + sf
    num = round(num, round_amt)
    if round_amt <= 0:
        num = int(num)

    return num


def digital_time(raw_time):
    if not isinstance(raw_time, int):
        return raw_time
    time = str(timedelta(milliseconds=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]

    return time
