'''
A pipeline module dedicated to extracting data from freely available news outlet APIs (e.g. the New York Times and the Guardian) to understand topic frequencies & trends.
'''

from .pipeline.transformer import transform
from .pipeline.resources import request_guardian_headlines, request_nyt_headlines
from .db import DatabaseConfig, DatabaseManager, BatchConfig