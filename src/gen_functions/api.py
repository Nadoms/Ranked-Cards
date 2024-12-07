import requests


def get(url: str, params: dict = None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
