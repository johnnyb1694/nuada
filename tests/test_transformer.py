import pandas as pd

from pandas.testing import assert_frame_equal
from nuada.transformer import _extract_headlines, _tokenize_headlines, _aggregate_terms

def test_headline_extraction(sample_nyt_json_decoded):
    """
    Testing that the correct key-value pairs are extracted from the decoded JSON response
    """
    expected = pd.DataFrame({
        'publication_date': [pd.to_datetime('2023-11-01T00:09:56+0000')],
        'headline': ['Fruit Flies Are Invading Los Angeles. The Solution? More Fruit Flies.'],
        'year': [2023],
        'month': [11]
    })
    actual = _extract_headlines(sample_nyt_json_decoded)
    assert_frame_equal(expected, actual, check_dtype=False)
