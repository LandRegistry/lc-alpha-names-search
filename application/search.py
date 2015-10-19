from elasticsearch import Elasticsearch
import logging


elastic = Elasticsearch()


def search(query):
    result = elastic.search(index='index', body=query)
    logging.info("Retrieved %d hits", result['hits']['total'])

    returns = []
    for item in result['hits']['hits']:
        new_item = item['_source']
        new_item['relevance'] = item['_score']
        returns.append(new_item)
    return returns


def phonetic_search(forename, surname):
    # Get matches based on the double-metaphone algorithm
    query = {
        'size': 100000000,
        'query': {
            'bool': {
                'must': [{
                    'match': {
                        'forenames.phonetic': {
                            'query': forename,
                            'operator': 'and'
                        }
                    }
                }, {
                    'match': {
                        'surname.phonetic': {
                            'query': surname
                        }
                    }
                }]
            }
        }
    }
    return search(query)


def distance_search(forename, surname):
    # Get matches based on the Levenstein distance algorithm
    forename_distance = round(len(forename) / 6)
    surname_distance = round(len(surname) / 3)

    query = {
        'size': 100000000,
        'query': {
            'bool': {
                'must': [
                    {
                        'match': {
                            'forenames': {
                                'query': forename,
                                'operator': 'and',
                                'fuzziness': str(forename_distance)
                            }
                        }
                    },
                    {
                        'match': {
                            'surname': {
                                'query': surname,
                                'fuzziness': str(surname_distance)
                            }
                        }
                    }
                ]
            }
        }
    }
    return search(query)


def combined_search(forename, surname):
    # Get results based on both algorithms
    forename_distance = round(len(forename) / 6)
    surname_distance = round(len(surname) / 3)
    query = {
        'size': 100000000,
        'query': {
            'bool': {
                'must': [
                    {
                        'bool': {
                            'should': [
                                {
                                    'match': {
                                        'surname': {
                                            'query': surname,
                                            'fuzziness': str(surname_distance)
                                        }
                                    }
                                },
                                {
                                    'match': {
                                        'surname.phonetic': {
                                            'query': surname
                                        }
                                    }
                                }
                            ],
                            'minimum_should_match': 1
                        }
                    },
                    {
                        'bool': {
                            'should': [
                                {
                                    'match': {
                                        'forenames': {
                                            'query': forename,
                                            'operator': 'and',
                                            'fuzziness': str(forename_distance)
                                        }
                                    }
                                },
                                {
                                    'match': {
                                        'forenames.phonetic': {
                                            'query': forename,
                                            'operator': 'and'
                                        }
                                    }
                                }
                            ],
                            'minimum_should_match': 1
                        }
                    }
                ]
            }
        }
    }
    return search(query)
