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


def get(directory_url: str, params: dict = None):
    url = API_URL + directory_url
    response = requests.get(url, headers=HEADERS, params=params)

    if response["status"] == "error":
        if response["data"] == "Too many requests":
            raise APIRateLimitError(url)
        elif response["data"] in NOT_FOUND_DATA:
            raise APINotFoundError(url)
        else:
            raise APIError(url)

    response.raise_for_status()
    return response.json()
