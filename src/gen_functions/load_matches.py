import asyncio
from os import path
import sys

package = path.join("src")
sys.path.insert(1, package)

from gen_functions import api


async def spam_redlime(start, limit):
    step_size = 200
    i = start
    new_additions = 0

    while True:
        print(f"Loading matches {i} to {i + step_size} / Total: {new_additions}")
        api.Match.load_db()
        k = 0
        try:
            matches = await asyncio.gather(
                *[
                    api.Match(id=j).get_async()
                    for j in range(i, i + step_size)
                ]
            )
            k += step_size
            if k >= limit:
                new_additions += api.Match.save_db()
                return
        except (api.APIRateLimitError, api.APIError):
            new_additions += api.Match.save_db()
            print("Rate limit reached, total loaded:", new_additions)
            await asyncio.sleep(600)
            k = 0
            continue

        new_additions += api.Match.save_db()
        i += step_size
        if matches == []:
            break

def main():
    asyncio.run(spam_redlime(1499237, 1000))

if __name__ == "__main__":
    main()
