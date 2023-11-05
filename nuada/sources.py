# New York Times: https://api.nytimes.com/svc/archive/v1/2022/9.json?api-key={KEY}

# The structure is roughly: {protocol}/{domain}/{resource}/{{params}}

import requests
import os

from dataclasses import dataclass
from typing import Any

@dataclass
class Source:
    """
    A 'Source' dataclass represents a news source (e.g. the 'New York Times' or otherwise).

    :param alias: a simple string-based tag for the specified source
    :param domain: a simple string-based description of the domain (e.g. 'api.nytimes.com')
    :param resource: a 'path' to the specific resource that can be found on the specified `domain` (e.g. 'svc/archive/v1/2022/09.json')
    :param params: a dictionary-based specification of HTTP 'GET' request parameters
    :param protocol: the selected protocol (defaults to 'https')
    """
    alias: str | None
    domain: str
    resource: str
    params: dict[str, Any]
    protocol: str = 'https'
    url = f'{protocol}://{domain}/{resource}'

def download_source(source: Source) -> requests.Response:
    try:
        res = requests.get(url=source.url, params=source.params)
        res.raise_for_status()
    except requests.exceptions.RequestException as re:
        print(f"Error: {re}")
        return None
    return res

# API: New York Times

def _construct_source_nyt(year: int, month: int, key: str = os.environ.get('SOURCE_KEY_NYT')) -> Source:
    """
    Constructs a dataclass for the New York Times specifically. Simple helper method.

    :param year: year of interest
    :param month: month of interest
    :param key: provided API key (secret credential that should be securely stored)
    """
    alias = 'New York Times ("Archive Search")'
    domain = 'api.nytimes.com'
    resource = f'svc/archive/v1/{str(year)}/{str(month)}.json'
    params = {'api-key': key}

    source_nyt = Source(alias, domain, resource, params)
    return source_nyt

def download_source_nyt(year: int, month: int, key: str = os.environ.get('SOURCE_KEY_NYT')) -> str:
    """
    Retrieves the raw response from the New York Times archive search API.

    :param year: year of interest
    :param month: month of interest
    :param key: provided API key (secret credential that should be securely stored)
    """
    source_nyt = _construct_source_nyt(year, month, key)
    res = download_source(source_nyt)
    return res

if __name__ == '__main__':
    pass
