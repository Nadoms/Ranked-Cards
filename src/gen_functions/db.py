from pathlib import Path
import sqlite3
from typing import Optional


def query_matches(
    cursor: sqlite3.Cursor,
    items: str = "*",
    id: Optional[int] = None,
    type: Optional[int] = None,
    season: Optional[int] = None,
    category: Optional[str] = None,
    gameMode: Optional[str] = None,
    date: Optional[int] = None,
    result_uuid: Optional[str] = None,
    time: Optional[int] = None,
    forfeited: Optional[bool] = None,
    decayed: Optional[bool] = None,
    seedType: Optional[str] = None,
    bastionType: Optional[str] = None,
    tag: Optional[str] = None,
    replayExist: Optional[bool] = None,
) -> list[any]:
    query = f"""
SELECT {items} FROM matches
WHERE
    (:id IS NULL OR id = :id) AND
    (:type IS NULL OR type = :type) AND
    (:season IS NULL OR season = :season) AND
    (:category IS NULL OR category = :category) AND
    (:gameMode IS NULL OR gameMode = :gameMode) AND
    (:date IS NULL OR date = :date) AND
    (:result_uuid IS NULL OR result_uuid = :result_uuid) AND
    (:time IS NULL OR time = :time) AND
    (:forfeited IS NULL OR forfeited = :forfeited) AND
    (:decayed IS NULL OR decayed = :decayed) AND
    (:seedType IS NULL OR seedType = :seedType) AND
    (:bastionType IS NULL OR bastionType = :bastionType) AND
    (:tag IS NULL OR tag = :tag) AND
    (:replayExist IS NULL OR replayExist = :replayExist)
    """

    params = {
        "id": id,
        "type": type,
        "season": season,
        "category": category,
        "gameMode": gameMode,
        "date": date,
        "result_uuid": result_uuid,
        "time": time,
        "forfeited": forfeited,
        "decayed": decayed,
        "seedType": seedType,
        "bastionType": bastionType,
        "tag": tag,
        "replayExist": replayExist,
    }

    cursor.execute(query, params)
    return cursor.fetchall()


def query_players(
    cursor: sqlite3.Cursor,
    items: str = "*",
    uuid: Optional[str] = None,
    nickname: Optional[str] = None,
) -> list[any]:
    query = f"""
SELECT {items} FROM players
WHERE
    (:uuid IS NULL OR uuid = :uuid) AND
    (:nickname IS NULL OR nickname = :nickname)
    """

    params = {
        "uuid": uuid,
        "nickname": nickname,
    }

    cursor.execute(query, params)
    return cursor.fetchall()


def query_match_players(
    cursor: sqlite3.Cursor,
    items: str = "*",
    match_id: Optional[int] = None,
    player_uuid: Optional[str] = None,
) -> list[any]:
    query = f"""
SELECT {items} FROM match_players
WHERE
    (:match_id IS NULL OR match_id = :match_id) AND
    (:player_uuid IS NULL OR player_uuid = :player_uuid)
    """

    params = {
        "match_id": match_id,
        "player_uuid": player_uuid,
    }

    cursor.execute(query, params)
    return cursor.fetchall()


def query_changes(
    cursor: sqlite3.Cursor,
    items: str = "*",
    match_id: Optional[int] = None,
    player_uuid: Optional[str] = None,
    change: Optional[int] = None,
    eloRate: Optional[int] = None,
) -> list[any]:
    query = f"""
SELECT {items} FROM changes
WHERE
    (:match_id IS NULL OR match_id = :match_id) AND
    (:player_uuid IS NULL OR player_uuid = :player_uuid) AND
    (:change IS NULL OR change = :change) AND
    (:eloRate IS NULL OR eloRate = :eloRate)
    """

    params = {
        "match_id": match_id,
        "player_uuid": player_uuid,
        "change": change,
        "eloRate": eloRate,
    }

    cursor.execute(query, params)
    return cursor.fetchall()


def query_timelines(
    cursor: sqlite3.Cursor,
    items: str = "*",
    match_id: Optional[int] = None,
    player_uuid: Optional[str] = None,
    time: Optional[int] = None,
    type: Optional[str] = None,
) -> list[any]:
    query = f"""
SELECT {items} FROM timelines
WHERE
    (:match_id IS NULL OR match_id = :match_id) AND
    (:player_uuid IS NULL OR player_uuid = :player_uuid) AND
    (:time IS NULL OR time = :time) AND
    (:type IS NULL OR type = :type)
    """

    params = {
        "match_id": match_id,
        "player_uuid": player_uuid,
        "time": time,
        "type": type,
    }

    cursor.execute(query, params)
    return cursor.fetchall()


def insert_match(
    cursor: sqlite3.Cursor,
    match: dict[str, any],
):
    cursor.execute(
        """
INSERT INTO matches (
    id,
    type,
    season,
    category,
    gameMode,
    result_uuid,
    time,
    forfeited,
    decayed,
    season,
    date,
    seedType,
    bastionType,
    tag,
    replayExist
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            match["id"],
            match["type"],
            match["season"],
            match["category"],
            match["gameMode"],
            match["result"]["uuid"],
            match["result"]["time"],
            match["forfeited"],
            match["decayed"],
            match["season"],
            match["date"],
            match["seedType"],
            match["bastionType"],
            match["tag"],
            match["replayExist"],
        )
    )

    for player in match["players"]:
        cursor.execute(
            """
INSERT OR IGNORE INTO players (
    uuid,
    nickname
) VALUES (?, ?)
            """,
            (
                player["uuid"],
                player["nickname"],
            )
        )
        cursor.execute(
            """
INSERT INTO match_players (
    match_id,
    player_uuid
) VALUES (?, ?)
            """,
            (
                match["id"],
                player["uuid"],
            )
        )

    if match["type"] == 2:
        for change in match["changes"]:
            cursor.execute(
                """ 
INSERT INTO changes (
    match_id,
    player_uuid,
    change,
    eloRate
) VALUES (?, ?, ?, ?)
                """,
                (
                    match["id"],
                    change["uuid"],
                    change["change"],
                    change["eloRate"],
                )
            )

    for event in match["timelines"]:
        cursor.execute(
            """
INSERT INTO timelines (
match_id,
player_uuid,
time,
type
) VALUES (?, ?, ?, ?)
            """,
            (
                match["id"],
                event["uuid"],
                event["time"],
                event["type"],
            )
        )


def init_db(cursor: sqlite3.Cursor):
    cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    type INTEGER,
    category TEXT,
    gameMode TEXT,
    result_uuid TEXT,
    time INTEGER,
    forfeited BOOLEAN,
    decayed BOOLEAN,
    season INTEGER,
    date INTEGER,
    seedType TEXT,
    bastionType TEXT,
    tag TEXT,
    replayExist BOOLEAN
)
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    uuid TEXT PRIMARY KEY,
    nickname TEXT
)
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS match_players (
    match_id INTEGER,
    player_uuid TEXT,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_uuid) REFERENCES players(uuid)
)
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS changes (
    match_id INTEGER,
    player_uuid TEXT,
    change INTEGER,
    eloRate INTEGER
)
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS timelines (
    match_id INTEGER,
    player_uuid TEXT,
    time INTEGER,
    type TEXT,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_uuid) REFERENCES players(uuid)
)
    """)


def start() -> sqlite3.Cursor:
    conn = sqlite3.connect((Path("src") / "database" / "ranked.db"))
    cursor = conn.cursor()
    return conn, cursor


def finish(conn: sqlite3.Connection):
    conn.commit()
    conn.close()


def main():
    conn, cursor = start()
    init_db(cursor)
    finish(conn)


if __name__ == "__main__":
    main()
