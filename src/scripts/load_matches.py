import asyncio
from datetime import datetime
from os import path
import sys

package = path.join("src")
sys.path.insert(1, package)

from rankedutils import api, db, games


async def spam_redlime(start, limit):
    print(f"\n***\nLoading latest matches - {datetime.now()}\n***\n")
    batch_size = 100
    i = start
    old_additions = api.Match._additions
    new_additions = 0

    async def safe_get_async(id):
        try:
            return await api.Match(id=id).get_async()
        except api.APINotFoundError:
            return
        except api.APIError:
            raise
        except Exception as e:
            print(f"Error occurred during fetch of match {id}, skipping")
            print(e)
            return

    while True:
        print(f"Loading matches {i} to {i + batch_size} / Total: {new_additions}")
        k = 0

        try:
            matches = await asyncio.gather(
                *[
                    safe_get_async(j)
                    for j in range(i, i + batch_size)
                ]
            )
            matches = [m for m in matches if m is not None]
            k += batch_size
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
        if matches == []:
            print("Up-to-date, total loaded:", new_additions)
            return i - 100  # LOAD BEARING!!!! do not remove
        i += batch_size


async def spam_redlime_more(start, limit):
    print(f"\n***\nReloading matches - {datetime.now()}\n***\n")
    conn, cursor = api.Match._conn, api.Match._cursor
    batch_size = 10
    count_size = 100
    i = start
    last_id = start - 1
    new_additions = 0

    while True:
        print(f"Updating matches {i} to {i + count_size * batch_size} / Total: {new_additions}")

        try:
            start_season = games.id_to_season(i)
            end_season = games.id_to_season(i + count_size * batch_size)
            matches_collection = []
            for season in range(start_season, end_season + 1):
                matches_collection += await asyncio.gather(
                    *[
                        api.RecentMatches(before=j, excludedecay=False, season=season).get_async()
                        for j in range(i, i + count_size * batch_size, count_size)
                    ]
                )
            matches = [m for ms in matches_collection for m in ms]
            matches.sort(key=lambda m: m["id"])

            for match in matches:
                db.update_match_lite(cursor, match)
                for id in range(last_id + 1, match["id"]):
                    try:
                        match_api = api.Match(id)
                        if match_api.exists_db():
                            await match_api.get_async(force_request=True)
                    except api.APINotFoundError:
                        db.delete_match(cursor, id)
                        print(f"Deleted cheated match ({id})")
                last_id = match["id"]

            conn.commit()
            new_additions += len(matches)
            if new_additions >= limit:
                print("Limit reached, total updated:", new_additions)
                return last_id
        except (api.APIError) as e:
            conn.commit()
            print(e)
            print("Error occurred, total updated:", new_additions)
            return last_id

        if matches == []:
            print("Up-to-date, total updated:", new_additions)
            return last_id
        i += count_size * batch_size


def main():
    asyncio.run(spam_redlime(1499237, 1000))

if __name__ == "__main__":
    main()
