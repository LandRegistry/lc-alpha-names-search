import os


class Config(object):
    DEBUG = False


class DevelopmentConfig(object):
    DEBUG = True
    SEARCH_TYPE = 'phonetic'  # distance, combined
    ELASTICSEARCH_URL = "http://localhost:9200"


class PreviewConfig(object):
    DEBUG = False
    SEARCH_TYPE = 'phonetic'
    ELASTICSEARCH_URL = "http://localhost:9200"
