# New York Times: https://api.nytimes.com/svc/archive/v1/2022/9.json?api-key={KEY}

# The structure is roughly: {protocol}/{domain}/{resource}/{{params}}

import requests
import os

from typing import Any

class Source:

    def __init__(self, alias: str | None, domain: str, resource: str, params: dict[str, Any], protocol: str = 'https'):
        """
        A 'Source' object represents a news source (e.g. the 'New York Times' or otherwise).

        :param alias: a simple string-based tag for the specified source
        :param domain: a simple string-based description of the domain (e.g. 'api.nytimes.com')
        :param resource: a 'path' to the specific resource that can be found on the specified `domain` (e.g. 'svc/archive/v1/2022/09.json')
        :param params: a dictionary-based specification of HTTP 'GET' request parameters
        :param protocol: the selected protocol (defaults to 'https')
        """
        self.alias = alias
        self._params = params
        self._url = f'{protocol}://{domain}/{resource}'

    def download(self) -> requests.Response:
        res = requests.get(url=self._url, params=self._params)
        res.raise_for_status()
        return res

def get_source_nyt_archive_search(year: int, month: int, key: str = os.environ.get('SOURCE_NYT_ARCHIVE_SEARCH')) -> Source:
    alias = 'New York Times ("Archive Search")'
    domain = 'api.nytimes.com'
    resource = f'svc/archive/v1/{str(year)}/{str(month)}.json'
    params = {'api-key': key}
    source_nyt = Source(alias, domain, resource, params)
    return source_nyt

if __name__ == '__main__':
    pass

