#encoding=utf-8
from sefaria.model import *
from pymongo import MongoClient
from sources.local_settings import *

client = MongoClient(MONGO_ASPAKLARIA_URL)
db = client.aspaklaria

# db.aspaklaria_source.insert_one({'topic': u'שלום', 'ref': "Genesis 1 1"})