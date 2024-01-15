import pandas as pd

from pandas.testing import assert_frame_equal
from nuada.pipeline.transformer import preprocess

def test_preprocess(sample_nyt_response):
    """
    Testing that the AWS response can be successfully processed and output a term frequency dataframe
    """
    actual = preprocess(sample_nyt_response)
    expected = pd.DataFrame({
        'term': ['headline', 'test'],
        'year': [2022, 2022],
        'month': [9, 9],
        'frequency': [1, 1]
    })
    assert_frame_equal(actual, expected, check_dtype=False)


