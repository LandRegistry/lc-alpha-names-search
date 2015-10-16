from elasticsearch import Elasticsearch
import logging


elastic = Elasticsearch()

#     result = elastic.search(index='index', body={'query': {'match_all': {}}}, size=1000000)
#
#     logging.info("Got %d hits", result['hits']['total'])
#     logging.info(result)
#
#     return_data = []
#     for hit in result['hits']['hits']:
#         return_data.append(hit['_source'])
#
#     return Response(json.dumps(return_data), status=200, mimetype='application/json')

def search(query):
    result = elastic.search(index='index', body=query)
    logging.info("Retrieved %d hits", result['hits']['total'])

    returns = []
    for item in result['hits']['hits']:
        returns.append(item['_source'])
    return returns


def phonetic_search(forename, surname):
    query = {
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
    forename_distance = round(len(forename) / 6)
    surname_distance = round(len(surname) / 3)

    query = {
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
    forename_distance = round(len(forename) / 6)
    surname_distance = round(len(surname) / 3)
    query = {
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
                    },
                    {
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
                    }
                ]
            }
        }
    }
    return search(query)
