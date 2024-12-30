from typing import Optional
import requests


API_URL = "https://mcsrranked.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0."
}
NOT_FOUND_DATA = [
    "User is not exists.",
    "match `id` is not found",
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
        self.url : str = f"{API_URL}{directory}?"

    def add(self, parameters: dict):
        formatted_parameters = []
        for key in parameters:
            if key is None:
                continue
            if parameters[key] == "":
                formatted_parameters.append(parameters["key"])
            else:
                formatted_parameters.append(f"{key}={parameters['key']}")
        self.url += "&".join(formatted_parameters)


    def get(directory_url: str) -> dict:
        url = API_URL + directory_url

        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
        except requests.exceptions.Timeout:
            raise APITimeoutError(url)

        if response["status"] == "error":
            if response["data"] == "Too many requests":
                raise APIRateLimitError(url)
            elif response["data"] in NOT_FOUND_DATA:
                raise APINotFoundError(url)
            else:
                raise APIError(url)

        return response.json()["data"]


class User(API):

    def __init__(
        self,
        name: str,
        *,
        season: Optional[int] = None,
    ):
        self.name = name
        self.season = season
        self.set_url()

    def set_url(self):
        self.url = f"users/{self.name}?"
        if self.season:
            self.url += f"season={self.season}"


class Matches(API):

    def __init__(
        self,
        page: int,
        count: int,
        type: int,
        season: int,
    ):
        self.page = page
        self.count = count
        self.type = type
        self.season = season


class RecentMatches(Matches):

    def __init__(
        self,
        *,
        page: Optional[int] = None,
        count: int = 50,
        type: Optional[int] = None,
        season: Optional[int] = None,
        excludedecay: bool = None,
    ):
        super().__init__(page=page, count=count, type=type, season=season)
        self.excludedecay = excludedecay


class UserMatches(Matches):

    def __init__(
        self,
        name: str,
        *,
        page: Optional[int] = None,
        count: int = 50,
        type: Optional[int] = None,
        season: Optional[int] = None,
        exclude_decay: bool = None,
    ):
        super().__init__(page=page, count=count, type=type, season=season)
        self.name = name
        self.exclude_decay = exclude_decay


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
        super().__init__(page=page, count=count, type=type, season=season)
        self.name_1 = name_1
        self.name_2 = name_2


class Match(API):

    def __init__(
        self,
        match_id: int,
    ):
        self.match_id = match_id


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
