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


def forename_phonetic_match(forename):
    return {
        'match': {
            'forenames.phonetic': {
                'query': forename,
                'operator': 'and'
            }
        }
    }


def forename_distance_match(forename, distance):
    return {
        'match': {
            'forenames': {
                'query': forename,
                'operator': 'and',
                'fuzziness': str(distance)
            }
        }
    }


def surname_phonetic_match(surname):
    return {
        'match': {
            'surname.phonetic': {
                'query': surname
            }
        }
    }


def surname_distance_match(surname, distance):
    return {
        'match': {
            'surname': {
                'query': surname,
                'fuzziness': str(distance)
            }
        }
    }


def es_and(query1, query2):
    return {
        'bool': {
            'must': [query1, query2]
        }
    }


def es_or(query1, query2):
    return {
        'bool': {
            'should': [query1, query2],
            'minimum_should_match': 1
        }
    }


def phonetic_search(forename, surname):
    logging.info('Phonetic Search')
    # Get matches based on the double-metaphone algorithm
    query = {
        'size': 100000000,
        'query': es_and(forename_phonetic_match(forename),
                        surname_phonetic_match(surname))

    }
    print(query)
    return search(query)


def distance_search(forename, surname):
    logging.info('Distance Search')
    # Get matches based on the Levenstein distance algorithm
    forename_distance = round(len(forename) / 6)
    surname_distance = round(len(surname) / 3)

    query = {
        'size': 100000000,
        'query': es_and(forename_distance_match(forename, forename_distance),
                        surname_distance_match(surname, surname_distance))
    }
    return search(query)


def combined_search(forename, surname):
    logging.info('Combined Search')
    # Get results based on both algorithms
    forename_distance = round(len(forename) / 6)
    surname_distance = round(len(surname) / 3)
    query = {
        'size': 100000000,
        'query': es_and(
            es_or(surname_distance_match(surname, surname_distance),
                  surname_phonetic_match(surname)),
            es_or(forename_distance_match(forename, forename_distance),
                  forename_phonetic_match(forename))
        )
    }
    return search(query)


def exact_search(full_name):
    query = {
        'size': 100000000,
        'query': {
            'filtered': {
                'query': {'match_all': {}},
                'filter': {
                    'term': {
                        'full_name': full_name
                    }
                }
            }
        }
    }
    return search(query)