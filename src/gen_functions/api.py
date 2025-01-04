import asyncio
from os import getenv
from typing import Optional
import aiohttp
from dotenv import load_dotenv
import requests


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
        try:
            response = requests.get(self.url, headers=HEADERS, timeout=5).json()
        except requests.exceptions.Timeout:
            raise APITimeoutError(self.url)

        if response["status"] == "error":
            if response["data"] == "Too many requests":
                raise APIRateLimitError(self.url)
            elif response["data"] in NOT_FOUND_DATA:
                raise APINotFoundError(self.url)
            else:
                raise APIError(self.url)

        return response["data"]

    async def get_async(self) -> dict[str, any]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url, headers=HEADERS, timeout=10) as fetch:
                    response = await fetch.json(content_type=None)
            except asyncio.TimeoutError:
                raise APITimeoutError(self.url)

        if response["status"] == "error":
            if response["data"] == "Too many requests":
                raise APIRateLimitError(self.url)
            elif response["data"] in NOT_FOUND_DATA:
                raise APINotFoundError(self.url)
            else:
                raise APIError(self.url)

        return response["data"]

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

    def __init__(
        self,
        id: int,
    ):
        self.id = id
        super().__init__(f"matches/{self.id}")


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
