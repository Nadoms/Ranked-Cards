import asyncio
from datetime import datetime
import json
from os import getenv
from pathlib import Path
import sqlite3
from typing import TextIO, Optional
import aiohttp
from dotenv import load_dotenv
import requests
from .db import *


ROOT = Path(__file__).parent.parent.parent.resolve()
MATCHES_FILE = ROOT / "src" / "database" / "matches.json"


load_dotenv()
API_KEY = getenv("API_KEY")
API_URL = "https://mcsrranked.com/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.",
    "API-Key": API_KEY,
}
NOT_FOUND_DATA = [
    "User is not exists.",
    "match `id` is not found",
    "race is not found",
]


class APIError(Exception):

    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f"APIError: {self.url}"


class APIRateLimitError(APIError):

    def __init__(self, url: str):
        super().__init__(url)

    def __str__(self):
        return f"APIRateLimitError: {self.url}"


class APINotFoundError(APIError):

    def __init__(self, url: str):
        super().__init__(url)

    def __str__(self):
        return f"APINotFoundError: {self.url}"


class APITimeoutError(APIError):

    def __init__(self, url: str):
        super().__init__(url)

    def __str__(self):
        return f"APITimeoutError: {self.url}"


class API():

    def __init__(
        self,
        directory: str,
    ):
        self.url : str = f"{API_URL}/{directory}?"

    def append(self, **kwargs: dict[str, any]):
        parameters = []
        for key in kwargs:
            if kwargs[key] is None:
                continue
            parameters.append(f"{key}={kwargs[key]}")
        self.url += "&" + "&".join(parameters)

    def get(self) -> dict[str, any]:
        cached_result = self._check_db()
        if cached_result is not None:
            return cached_result

        try:
            response = requests.get(self.url, headers=HEADERS, timeout=5).json()
        except requests.exceptions.Timeout:
            raise APITimeoutError(self.url)

        return self._handle_response(response)

    async def get_async(self) -> dict[str, any]:
        cached_result = self._check_db()
        if cached_result is not None:
            return cached_result

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url, headers=HEADERS, timeout=10) as fetch:
                    response = await fetch.json(content_type=None)
            except asyncio.TimeoutError:
                raise APITimeoutError(self.url)

        return self._handle_response(response)

    def _handle_response(self, response: dict[str, any]) -> dict[str, any]:
        if response["status"] == "error":
            if response["data"] == "Too many requests":
                raise APIRateLimitError(self.url)
            elif response["data"] in NOT_FOUND_DATA:
                raise APINotFoundError(self.url)
            else:
                raise APIError(self.url)

        self._save_result(response["data"])
        return response["data"]

    def _save_result(self, data: dict[str, any]):
        pass

    def _check_db(self):
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.url}"


class User(API):

    def __init__(
        self,
        name: str,
        *,
        season: Optional[int] = None,
    ):
        self.name = name
        self.season = season
        super().__init__(f"users/{self.name}")
        self.append(season=self.season)


class Matches(API):

    def __init__(
        self,
        directory: str,
        page: int,
        count: int,
        type: int,
        season: int,
    ):
        self.page = page
        self.count = count
        self.type = type
        self.season = season
        super().__init__(directory)
        self.append(
            page=self.page,
            count=self.count,
            type=self.type,
            season=self.season
        )


class RecentMatches(Matches):

    def __init__(
        self,
        *,
        page: Optional[int] = None,
        count: int = 50,
        type: Optional[int] = None,
        season: Optional[int] = None,
        excludedecay: bool = True,
    ):
        self.excludedecay = excludedecay
        super().__init__(
            directory="matches",
            page=page,
            count=count,
            type=type,
            season=season
        )
        self.append(excludedecay=self.excludedecay)


class UserMatches(Matches):

    def __init__(
        self,
        name: str,
        *,
        page: Optional[int] = None,
        count: int = 50,
        type: Optional[int] = None,
        season: Optional[int] = None,
        excludedecay: bool = True,
    ):
        self.name = name
        self.excludedecay = excludedecay
        super().__init__(
            directory=f"users/{self.name}/matches",
            page=page,
            count=count,
            type=type,
            season=season
        )
        self.append(excludedecay=self.excludedecay)


class VersusMatches(Matches):

    def __init__(
        self,
        name_1: str,
        name_2: str,
        *,
        page: Optional[int] = None,
        count: int = 50,
        type: Optional[int] = None,
        season: Optional[int] = None,
    ):
        self.name_1 = name_1
        self.name_2 = name_2
        super().__init__(
            directory=f"users/{self.name_1}/versus/{self.name_2}/matches",
            page=page,
            count=count,
            type=type,
            season=season
        )


class Match(API):
    _additions: int = 0
    _conn: sqlite3.Connection
    _cursor: sqlite3.Cursor = None

    def __init__(
        self,
        id: int,
    ):
        self.id = id
        super().__init__(f"matches/{self.id}")

    def _save_result(self, data: dict[str, any]):
        insert_match(Match._cursor, data)
        Match._additions += 1

    def _check_db(self) -> dict[str, any]:
        if not Match._cursor:
            return None

        match = query_db(Match._cursor, id=self.id)
        if not match:
            return None

        runs = query_db(
            Match._cursor,
            table="runs",
            match_id=self.id
        )

        uuids = [run[1] for run in runs]
        players = []
        for uuid in uuids:
            players += query_db(
                Match._cursor,
                table="players",
                uuid=uuid
            )

        return self._convert(match[0], players, runs)

    def _convert(
        self,
        match: list[any],
        players: list[any],
        runs: list[any],
    ) -> dict[str, any]:
        players = [
            {
                "uuid": player[0],
                "nickname": player[1],
            }
            for player in players
        ]

        changes = [
            {
                "uuid": run[1],
                "change": run[2],
                "eloRate": run[3],
            }
            for run in runs
        ]

        timelines = []
        for run in runs:
            timelines += [
            {
                "uuid": run[1],
                "time": event["time"],
                "type": event["type"],
            }
            for event in json.loads(run[4])
        ]
        timelines.sort(key=lambda x: x["time"], reverse=True)

        return {
            "id": match[0],
            "type": match[1],
            "category": match[2],
            "gameMode": match[3],
            "players": players,
            "result": {
                "uuid": match[4],
                "time": match[5],
            },
            "forfeited": bool(match[6]),
            "decayed": bool(match[7]),
            "changes": changes,
            "timelines": timelines,
            "season": match[8],
            "date": match[9],
            "seedType": match[10],
            "bastionType": match[11],
            "tag": match[12],
            "replayExist": match[13],
        }

    @classmethod
    def load_db(cls):
        cls._conn = sqlite3.connect(Path("src") / "database" / "ranked.db")
        cls._cursor = cls._conn.cursor()
        cls._additions = 0

    @classmethod
    def save_db(cls):
        cls._conn.commit()
        cls._conn.close()
        cls._cursor = None
        cls._cache = {}
        return cls._additions


class Versus(API):

    def __init__(
        self,
        name_1: str,
        name_2: str,
        *,
        season: Optional[int] = None,
    ):
        self.name_1 = name_1
        self.name_2 = name_2
        super().__init__(f"users/{self.name_1}/versus/{self.name_2}")
        self.append(season=season)


class WeeklyRace(API):

    def __init__(
        self,
        *,
        id: Optional[int] = None,
    ):
        self.id = id
        super().__init__(f"weekly-race/{self.id}")
