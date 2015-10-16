import os


class Config(object):
    DEBUG = False


class DevelopmentConfig(object):
    DEBUG = True
    SEARCH_TYPE = 'phonetic'  # distance, combined


class PreviewConfig(object):
    DEBUG = False
    SEARCH_TYPE = 'phonetic'
