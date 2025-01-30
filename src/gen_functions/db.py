import json
from pathlib import Path
import sqlite3
from typing import Optional


DEFAULT_DB = (Path("src") / "database" / "ranked.db")


def query_db(
    cursor: sqlite3.Cursor,
    table: str = "matches",
    items: str = "*",
    order: Optional[str] = None,
    limit: Optional[int] = None,
    debug: bool = False,
    **kwargs: any,
) -> list[any]:
    conditions = []

    for key in kwargs:
        conditions.append(f"{key} = :{key}")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else "1=1"
    order_clause = f"ORDER BY {order}" if order else ""
    limit_clause = f"LIMIT {limit}" if limit else ""

    query = f"""
SELECT {items} FROM {table}
{where_clause}
{order_clause}
{limit_clause}
    """

    if debug:
        cursor.execute(f"EXPLAIN QUERY PLAN {query}", kwargs)
        print(cursor.fetchone())

    cursor.execute(query, kwargs)
    return cursor.fetchall()


def get_elo(
    cursor: sqlite3.Cursor,
    uuid: str,
) -> Optional[int]:
    run = query_db(
        cursor,
        "runs",
        items="eloRate, change",
        order="match_id DESC",
        limit=1,
        player_uuid=uuid
    )
    if not run:
        return None
    run = run[0]
    current_elo = run[0] + run[1]
    return current_elo


def get_sb(
    cursor: sqlite3.Cursor,
    uuid: str,
) -> Optional[int]:
    match = query_db(
        cursor,
        "matches",
        items="time",
        order="time ASC",
        limit=1,
        result_uuid=uuid,
        forfeited=False,
    )
    if match:
        return match[0][0]


def insert_match(
    cursor: sqlite3.Cursor,
    match: dict[str, any],
):
    if not cursor:
        return

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

    for change in match["changes"]:
        timeline = [
            {
                "time": event["time"],
                "type": event["type"],
            }
            for event in match["timelines"]
            if event["uuid"] == change["uuid"]
        ]
        timeline_json = json.dumps(timeline)
        cursor.execute(
            """
INSERT INTO runs (
    match_id,
    player_uuid,
    change,
    eloRate,
    timeline
) VALUES (?, ?, ?, ?, ?)
            """,
            (
                match["id"],
                change["uuid"],
                change["change"],
                change["eloRate"],
                timeline_json,
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
CREATE TABLE IF NOT EXISTS runs (
    match_id INTEGER,
    player_uuid TEXT,
    change INTEGER,
    eloRate INTEGER,
    timeline TEXT,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_uuid) REFERENCES players(uuid)
)
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_id ON runs (match_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_uuid ON runs (player_uuid)")


def start(db_path: Path = DEFAULT_DB) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(db_path)
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
