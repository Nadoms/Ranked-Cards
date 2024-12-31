import asyncio
import json
from os import getenv
from pathlib import Path
from typing import TextIO, Optional
import aiohttp
from dotenv import load_dotenv
import requests


ROOT = Path(__file__).parent.parent.parent.resolve()
MATCHES_FILE = ROOT / "src" / "database" / "matches.json"


load_dotenv()
API_KEY = getenv("API_KEY")
API_URL = "https://mcsrranked.com/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0."
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
        self.url : str = f"{API_URL}/{directory}?API-Key={API_KEY}"

    def append(self, **kwargs: dict[str, any]):
        parameters = []
        for key in kwargs:
            if kwargs[key] is None:
                continue
            parameters.append(f"{key}={kwargs[key]}")
        self.url += "&" + "&".join(parameters)

    def get(self) -> dict[str, any]:
        cached_result = self._check_cache()
        if cached_result is not None:
            return cached_result

        try:
            response = requests.get(self.url, headers=HEADERS, timeout=5).json()
        except requests.exceptions.Timeout:
            raise APITimeoutError(self.url)

        return self._handle_response(response)

    async def get_async(self) -> dict[str, any]:
        cached_result = self._check_cache()
        if cached_result is not None:
            return cached_result

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url, headers=HEADERS, timeout=10) as fetch:
                    response = await fetch.json()
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

        self._cache_result(response["data"])
        return response["data"]

    def _cache_result(self, data: dict[str, any]):
        pass

    def _check_cache(self):
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
    _cache: dict[str, any] = {}
    _additions: int = 0

    def __init__(
        self,
        id: int,
    ):
        self.id = id
        super().__init__(f"matches/{self.id}")

    def _cache_result(self, data: dict[str, any]):
        Match._cache[str(self.id)] = data
        Match._additions += 1

    def _check_cache(self) -> dict[str, any]:
        data = Match._cache.get(str(self.id))
        return data

    @classmethod
    def load_cache(cls):
        cls._cache = json.loads(MATCHES_FILE.read_text())
        cls._additions = 0

    @classmethod
    def dump_cache(cls):
        MATCHES_FILE.write_text(json.dumps(cls._cache, indent=4, sort_keys=True))
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
