"""
A project dedicated to extracting data from freely available news outlet APIs (e.g. the New York Times and the Guardian) to understand topic frequencies & trends.
"""

from .transformer import preprocess
from .db import DBC, init_db, ingest
from .models import Control
from .resources import request_nyt_archive_search
