import requests
import pandas as pd

class Resource():

    def __init__(self, url: str, params: dict):
        self.url = url
        self.params = params
        self.response = None

    def load(self):
        try:
            response = requests.get(self.url, self.params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise e
        else:
            self.response = response.json()

    def __repr__(self):
        return f'Resource @ "{self.url}"'

class NewYorkTimes(Resource):

    def __init__(self, year: int, month: int, nyt_key: str):
        nyt_url = f'https://api.nytimes.com/svc/archive/v1/{str(year)}/{str(month)}.json'
        super().__init__(url=nyt_url, params={'api-key': nyt_key})

    def preprocess(self) -> pd.DataFrame:

        articles = self.response_raw['response']['docs']

        headlines = [{'publication_date': pd.to_datetime(article['pub_date']),
                      'headline': article['headline']['main']} for article in articles]
        
        headlines_df = pd.DataFrame(headlines)
        headlines_df['year'] = headlines_df['publication_date'].dt.year
        headlines_df['month'] = headlines_df['publication_date'].dt.month
        return headlines_df

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
    nyt = NewYorkTimes(2023, 11, 'ePMmMmWGTVXZozP9iIzwTVqEYLyoRCuv')
    nyt_headlines = nyt.load().preprocess()