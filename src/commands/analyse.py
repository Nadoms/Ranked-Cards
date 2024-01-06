from analyse_functions import add_names, add_shapes, add_stats, add_skins, add_splits, add_context, add_pentagon, add_other

import requests
from PIL import Image
from os import path
from datetime import datetime

def main(response, match_id):
    response = response["data"]
    names = [response["members"][0]["nickname"], response["members"][1]["nickname"]]
    uuids = [response["members"][0]["uuid"], response["members"][1]["uuid"]]

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    vs_response = requests.get(f"https://mcsrranked.com/api/users/{names[0]}/versus/{names[1]}", headers=headers).json()
    print(f"https://mcsrranked.com/api/users/{names[0]}/versus/{names[1]}")
    print(uuids)
    if vs_response["status"] != "success":
        return -1
    vs_response = vs_response["data"]

    file = path.join("src", "pics", "bgs", "nether.jpg")
    analysis = Image.open(file)

    then = datetime.now()
    analysis = add_shapes.write(analysis, names, response) # done! for now
    then = splits(then, 0)
    analysis = add_names.write(analysis, names, response) # done!
    then = splits(then, 1)
    analysis = add_stats.write(analysis, uuids, response, vs_response) # yup!
    then = splits(then, 2)
    analysis = add_skins.write(analysis, uuids) # yes!
    then = splits(then, 3)
    analysis = add_splits.write(analysis, uuids, response, match_id) # oh dear god...
    then = splits(then, 4)
    analysis = add_context.write(analysis, names, response, match_id)
    then = splits(then, 5)
    analysis = add_pentagon.write(analysis, names, response, match_id)
    then = splits(then, 6)
    analysis = add_other.write(analysis)
    then = splits(then, 7)

    return analysis

def splits(then, process):
    processes = ["Drawing boxes",
     "Writing usernames",
     "Calculating stats",
     "Finding skins",
     "Comparing splits",
     "Generating context",
     "Pentagoning pentgagon",
     "Final touchups"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now

if __name__ == "__main__":
    input_name = "nadoms"
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}").json()
    type = "elo"
    main(input_name, response, type).show()