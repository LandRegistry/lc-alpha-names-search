from elasticsearch import Elasticsearch
import logging
import pprint


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


def es_or(query_list):
    return {
        'bool': {
            'should': query_list
        }
    }


def get_search_body(term):
    return {
        'size': 100000000,
        'query': {
            'filtered': {
                'query': {'match_all': {}},
                'filter': {
                    'term': term
                }
            }
        }
    }


def exact_search_full(full_name):
    query = get_search_body({'full_name': full_name})
    return search(query)


def exact_search_structured(name):
    # Generate variants of the full name by squashing adjecent forenames together
    forenames = []
    for i in range(len(name['forenames']) - 1):
        before = name['forenames'][0:i]
        after = name['forenames'][i + 2:]
        combine = name['forenames'][i:i + 2]
        fn = ' '.join(before) + ' ' + ''.join(combine) + ' ' + ' '.join(after)
        forenames.append(fn.strip())

    fullname = ' '.join(name['forenames']) + ' ' + name['surname']
    search_array = [{"match": {"full_name": fullname}}]
    for forename in forenames:
        search_name = forename + ' ' + name['surname']
        search_array.append({"match": {"full_name": search_name}})

    query = {
        'size': 100000000,
        'query': es_or(search_array)
    }
    return search(query)


def get_for_title_number(title):
    query = get_search_body({'title_number': title})
    return elastic.search(index='index', body=query)['hits']['hits']
