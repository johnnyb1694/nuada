import requests
import os
import json

def request_nyt_archive_search(year: int, month: int, key: str) -> str:
    """
    Request results of the New York Times 'Archive Search' API (NYT API) via the internet.

    :param year: Year of interest
    :param month: Month of interest
    :param key: API key applicable to the NYT API
    """
    if not key:
        raise ValueError('Input variable `key` must be specified')
    
    url = f'https://api.nytimes.com/svc/archive/v1/{str(year)}/{str(month)}.json?api-key={key}'
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise e
    return res.json()

if __name__ == '__main__':
    pass
