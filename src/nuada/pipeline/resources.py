import requests
import pandas as pd
import time
import logging
import itertools

from datetime import datetime, timedelta
from requests.exceptions import RequestException

def request(url: str, params: dict, delay: int = 0):
    '''
    Wrapper function which calls `requests.get()` under the hood
    '''
    if delay > 0:
        logging.info(f'Sleeping for {delay} seconds prior to making GET request (endpoint: {url})')
        time.sleep(delay)
    res = requests.get(url, params)
    res.raise_for_status()
    deserialised = res.json()
    return deserialised

def get_date_range(year: int, month: int):
    '''
    For a given year and month, this function returns the 'start' and 'end' dates that enclose that specific month
    '''
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start.date(), end.date()

def standardise_guardian_headlines(res_deserialised: dict):
    '''
    Ingest raw JSON response from the Guardian API resource (`deserialised`) and standardise into a list of
    dictionaries with fields: `publication_date` and `headline`
    '''
    articles = res_deserialised['response']['results']
    headlines = [{'publication_date': pd.to_datetime(article['webPublicationDate']),
                  'headline': article['webTitle']} for article in articles]
    return headlines

def standardise_nyt_headlines(res_deserialised: dict):
    '''
    Ingest raw JSON response from the New York Times API resource (`deserialised`) and standardise into a list of
    dictionaries with fields: `publication_date` and `headline`
    '''
    articles = res_deserialised['response']['docs']
    headlines = [{'publication_date': pd.to_datetime(article['pub_date']),
                  'headline': article['headline']['main']} for article in articles]
    return headlines

def request_nyt_headlines(year: int, month: int, key: str) -> str:
    '''
    Get all of the headlines from the New York Times for a specific `year` & `month`

    :param year: Year of interest
    :param month: Month of interest
    :param key: Developer key for New York Times API service
    '''
    if not key:
        raise ValueError('Input variable `key` must be specified')
    url = f'https://api.nytimes.com/svc/archive/v1/{str(year)}/{str(month)}.json'
    params = {'api-key': key}
    try:
        res = request(url, params)
        headlines = standardise_nyt_headlines(res)
    except RequestException as err:
        raise err
    return headlines

def impute_param(params: dict, key: str, value):
    params[key] = value
    return params

def request_guardian_headlines(year: int, month: int, key: str, n_pages: int | None = None) -> str:
    '''
    Get all of the headlines from the Guardian for a specific `year` & `month`

    :param year: Year of interest
    :param month: Month of interest
    :param key: Developer key for Guardian API service
    '''
    if not key:
        raise ValueError('Input variable `key` must be specified')
    start_date, end_date = get_date_range(year, month)
    url = 'https://content.guardianapis.com/search'
    params = {'api-key': key,
              'page': 1,
              'page-size': 50,
              'from-date': str(start_date),
              'to-date': str(end_date)}
    try:
        if not n_pages:
            init_res = request(url, params)
            n_pages = init_res['response']['pages'] # NB: retrieves the number of pages
        headline_list = []
        for n in range(1, n_pages + 1):
            params['page'] = n
            res = request(url, params, delay = 0.50)
            headlines = standardise_guardian_headlines(res)
            headline_list.append(headlines)
        headlines = list(itertools.chain.from_iterable(headline_list))
    except RequestException as err:
        raise err
    return headlines

if __name__ == '__main__':
    pass