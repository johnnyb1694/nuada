import pandas as pd
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def _download_nltk_data(download_dir: str = '/tmp') -> None:
    '''
    Helper function to download pre-requisite tokenizer artifacts for tokenization purposes.
    '''
    try:
        nltk.data.path.append(download_dir)
        nltk.download('punkt', quiet=True, download_dir=download_dir)
        nltk.download('stopwords', quiet=True, download_dir=download_dir)
    except IOError as err:
        raise err

def _tokenize_headlines(headlines_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Ingests dataframe of headlines and expands each 'term' contained within the headline into a separate row.

    :param headlines_df: `pd.DataFrame` object with *at least* column `headline`
    '''
    headlines_df['term'] = headlines_df['headline'].apply(word_tokenize)
    terms_df = headlines_df.explode('term')
    terms_df['term'] = terms_df['term'].str.lower()

    stop_words = set(stopwords.words('english')) # NB: set-based usage improves lookup efficiency over list-based usage
    terms_df = terms_df[~terms_df['term'].isin(stop_words)]
    terms_df = terms_df[terms_df['term'].apply(lambda xx: xx.isalpha())]
    return terms_df

def _aggregate_terms(terms_df: pd.DataFrame, grain: list[str] = ['term', 'year', 'month']) -> pd.DataFrame:
    '''
    Aggregate headline terms by the list of strings specified in `by`

    :param terms_df: `pd.DataFrame` object with *at least* columns `term`, `year` and `month`
    '''
    aggregation = terms_df.groupby(by=grain).size().reset_index(name='frequency')
    return aggregation

def transform(headlines_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Transform a `headlines_df` object (as implemented in `nuada.pipeline.resources`) into a tokenized term-frequency matrix
    '''
    _download_nltk_data()
    terms_df = headlines_df.pipe(_tokenize_headlines).pipe(_aggregate_terms)
    return terms_df

if __name__ == '__main__':  
    pass
