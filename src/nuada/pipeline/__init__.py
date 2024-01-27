"""
A project dedicated to extracting data from freely available news outlet APIs (e.g. the New York Times and the Guardian) to understand topic frequencies & trends.
"""

from nuada.pipeline.transformer import preprocess
from nuada.pipeline.db import DBC, init_db, ingest
from nuada.models import Control
from nuada.pipeline.resources import request_nyt_archive_search
