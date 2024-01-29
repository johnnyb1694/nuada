import pandas as pd
from nuada.pipeline.transformer import _download_nltk_data, _tokenize_headlines, _aggregate_terms, transform

def test_download_nltk_data(tmp_path):
    '''
    Verifies that `nltk` data can be initialised successfully
    '''
    download_dir = tmp_path / 'nltk_data'
    _download_nltk_data(download_dir)
    assert (download_dir / 'corpora' / 'stopwords.zip').is_file()
    assert (download_dir / 'tokenizers' / 'punkt.zip').is_file()

def test_tokenize_headlines(sample_headlines_df):
    '''
    Tests that headline terms can be tokenized appropriately and without numeric or punctual inclusions
    '''
    terms_df = _tokenize_headlines(sample_headlines_df)
    
    assert 'term' in terms_df.columns
    assert terms_df['term'].str.isalpha().all()

def test_aggregate_terms(sample_headlines_df):
    '''
    Tests that aggregations can be performed as expected and with fully populated frequencies
    '''
    terms_df = _tokenize_headlines(sample_headlines_df)
    aggregated_df = _aggregate_terms(terms_df)
    
    assert 'frequency' in aggregated_df.columns
    assert not aggregated_df['frequency'].isnull().any()

def test_transform(sample_headlines_df):
    '''
    Tests that the end-to-end transformation process works as expected
    '''
    aggregated_df = transform(sample_headlines_df)
    
    # Check that required fields are generated and reasonably populated
    assert 'frequency' in aggregated_df.columns
    assert not aggregated_df['frequency'].isnull().any()
    # Check that the frequency is calculated properly for a given headline
    assert aggregated_df.loc[aggregated_df['term'] == 'apple', 'frequency'].values[0] == 2
    assert aggregated_df.loc[aggregated_df['term'] == 'orange', 'frequency'].values[0] == 2
    assert aggregated_df.loc[aggregated_df['term'] == 'banana', 'frequency'].values[0] == 3

if __name__ == '__main__':
    pass
