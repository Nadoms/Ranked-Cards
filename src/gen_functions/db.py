from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import Optional

from gen_functions import constants


PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = PROJECT_DIR / "database" / "ranked.db"


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
    season: int = constants.SEASON,
) -> Optional[int]:
    run = query_db(
        cursor,
        "runs",
        items="eloRate, change, match_id",
        order="match_id DESC",
        limit=1,
        player_uuid=uuid
    )
    if not run:
        return None
    run = run[0]
    if not run[0]:
        return None
    match = query_db(
        cursor,
        "matches",
        items="season",
        limit=1,
        id=run[2]
    )[0]
    if int(match[0]) != season:
        return None
    current_elo = run[0] + run[1]
    return current_elo


def get_sb(
    cursor: sqlite3.Cursor,
    uuid: str,
    season: int = constants.SEASON,
) -> Optional[int]:
    match = query_db(
        cursor,
        "matches",
        items="time",
        order="time ASC",
        limit=1,
        type=2,
        result_uuid=uuid,
        forfeited=False,
        season=season,
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
            match.get("id"),
            match.get("type"),
            match.get("season"),
            match.get("category"),
            match.get("gameMode"),
            match["result"].get("uuid"),
            match["result"].get("time"),
            match.get("forfeited"),
            match.get("decayed"),
            match.get("season"),
            match.get("date"),
            match.get("seedType"),
            match.get("bastionType"),
            match.get("tag"),
            match.get("replayExist"),
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
                player.get("uuid"),
                player.get("nickname"),
            )
        )

    for player in match["players"]:
        timeline = [
            {
                "time": event.get("time"),
                "type": event.get("type"),
            }
            for event in match["timelines"]
            if event.get("uuid") == player.get("uuid")
        ]
        timeline_json = json.dumps(timeline)
        change = next((change for change in match["changes"] if change.get("uuid") == player.get("uuid")), {})
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
                match.get("id"),
                player.get("uuid"),
                change.get("change"),
                change.get("eloRate"),
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
    replayExist BOOLEAN,
    seed_id TEXT
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

    cursor.execute("""
CREATE TABLE IF NOT EXISTS seeds (
    id TEXT PRIMARY KEY,
    seed_type TEXT,
    bastion_type TEXT,
    front_diag INTEGER,
    front_straight INTEGER,
    back_diag INTEGER,
    back_straight INTEGER,
    o_level INTEGER,
    triples INTEGER,
    singles INTEGER,
    small_singles INTEGER,
    bastion_biome TEXT,
    fortress_biome TEXT,
    stucture_biome TEXT
)
    """)


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
