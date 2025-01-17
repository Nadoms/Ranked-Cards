import asyncio
from os import path
import sys

package = path.join("src")
sys.path.insert(1, package)

from gen_functions import api


S7_START = 1499237


async def spam_redlime():
    step_size = 200
    big_step_size = 1000
    i = S7_START
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
            if k > big_step_size:
                raise api.APIError()
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
    asyncio.run(spam_redlime())

if __name__ == "__main__":
    main()
