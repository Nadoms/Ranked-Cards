import asyncio
from datetime import datetime
from os import path
import sys

package = path.join("src")
sys.path.insert(1, package)

from rankedutils import api


async def spam_redlime(start, limit):
    print(f"\n***\nLoading latest matches - {datetime.now()}\n***\n")
    step_size = 100
    i = start
    old_additions = api.Match._additions
    new_additions = 0

    async def safe_get_async(id):
        try:
            return await api.Match(id=id).get_async()
        except (api.APINotFoundError):
            return None

    while True:
        print(f"Loading matches {i} to {i + step_size} / Total: {new_additions}")
        k = 0

        try:
            matches = await asyncio.gather(
                *[
                    safe_get_async(j)
                    for j in range(i, i + step_size)
                ]
            )
            matches = [m for m in matches if m is not None]
            k += step_size
            if new_additions >= limit:
                new_additions = api.Match.commit() - old_additions
                print("Limit reached, total loaded:", new_additions)
                return i
        except (api.APIError) as e:
            new_additions = api.Match.commit() - old_additions
            print(e)
            print("Error occurred, total loaded:", new_additions)
            return i

        new_additions = api.Match.commit() - old_additions
        i += step_size
        if matches == []:
            return i

def main():
    asyncio.run(spam_redlime(1499237, 1000))

if __name__ == "__main__":
    main()
