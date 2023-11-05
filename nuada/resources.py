import requests
import os

from typing import Any

def download_resource(url: str, params: dict[str, Any]) -> requests.Response:
    """
    Generic helper function for downloading 'resources' from the internet (e.g. via a suitable REST API)

    :param url: the location of the resource that the user would like to download
    :param params: the HTTP request parameters that must be injected into the request call corresponding to the `url` specification
    """
    try:
        res = requests.get(url, params)
        res.raise_for_status()
    except requests.exceptions.RequestException as re:
        print(f"Error: {re}")
        return None
    return res.json()

def download_resource_nyt(year: int, month: int, key: str = os.environ.get('SOURCE_KEY_NYT')) -> str:
    """
    Specific function which leverages `download_resource()` to acquire the results of the New York Times 'Archive Search' API via the internet

    :param year: year of interest
    :param month: month of interest
    :param key: the API key applicable to this application
    """
    if not key:
        raise ValueError('Input variable `key` must be specified')
    url = f'https://api.nytimes.com/svc/archive/v1/{str(year)}/{str(month)}.json'
    params = {'api-key': key}
    res = download_resource(url, params)
    return res

if __name__ == '__main__':
    
    # Example call to the NYT 'Archive Search' API
    articles = download_resource_nyt(2022, 9)

    print(articles)
