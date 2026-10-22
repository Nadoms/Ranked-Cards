import sys
from datetime import datetime

import matplotlib.dates as md
import matplotlib.pyplot as plt

times, rss, swap = [], [], []
for line in open(sys.argv[1]):
    fields = line.split()
    times.append(datetime.strptime(fields[0], "%H:%M:%S"))
    rss.append(int(fields[1]) / 1024)
    swap.append(int(fields[-2]))

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(times, rss, drawstyle="steps-post", label="Bot RSS")
ax.plot(times, swap, drawstyle="steps-post", label="Swap used")
ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
ax.set(xlabel="Time", ylabel="MB")
ax.legend()
fig.savefig(sys.argv[2], dpi=120)
