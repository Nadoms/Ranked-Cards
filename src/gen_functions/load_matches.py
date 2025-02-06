import asyncio
from os import path
import sys

package = path.join("src")
sys.path.insert(1, package)

from gen_functions import api


async def spam_redlime(start, limit):
    step_size = 100
    i = start
    old_additions = api.Match._additions
    new_additions = 0

    while True:
        print(f"Loading matches {i} to {i + step_size} / Total: {new_additions}")
        k = 0

        try:
            matches = await asyncio.gather(
                *[
                    api.Match(id=j).get_async()
                    for j in range(i, i + step_size)
                ]
            )
            k += step_size
            if new_additions >= limit:
                new_additions = api.Match.commit() - old_additions
                print("Limit reached, total loaded:", new_additions)
                return i
        except (api.APIRateLimitError, api.APIError):
            new_additions = api.Match.commit() - old_additions
            print("Rate limit reached, total loaded:", new_additions)
            return i

        new_additions = api.Match.commit() - old_additions
        i += step_size
        if matches == []:
            return i

def main():
    asyncio.run(spam_redlime(1499237, 1000))

if __name__ == "__main__":
    main()
