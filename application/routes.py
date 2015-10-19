from application import app
from flask import Response, request
from application.search import elastic, phonetic_search, distance_search, combined_search
import logging
import json
import requests


@app.route('/', methods=["GET"])
def index():
    return Response(status=200)


@app.route('/health', methods=['GET'])
def healthcheck():
    result = {
        'status': 'OK',
        'dependencies': []
    }

    es_response = requests.get(app.config['ELASTICSEARCH_URL'])
    if es_response.status_code == 200:
        status = 200
    else:
        status = 500
    result['dependencies'].append({
        'elasticsearch': str(es_response.status_code) + ' ' + es_response.reason
    })

    return Response(json.dumps(result), status=status, mimetype='application/json')


@app.route('/names', methods=['POST'])
def add_index_entry():
    if request.headers['Content-Type'] != "application/json":
        return Response(status=415)

    data = request.get_json(force=True)

    logging.info(data)

    for item in data:
        # Data structure coming in isn't quite how we want to index it...
        index_item = {
            'title_number': item['title_number'],
            'office': item['office'],
            'sub_register': item['sub_register'],
            'name_type': item['name_type']
        }

        if item['name_type'] == 'Private':
            index_item['forenames'] = " ".join(item['registered_proprietor']['forenames'])
            index_item['surname'] = item['registered_proprietor']['surname']
            index_item['full_name'] = index_item['forenames'] + ' ' + index_item['surname']

        result = elastic.index(index='index', doc_type='names', body=index_item)
        logging.info(result['created'])
    elastic.indices.refresh(index="index")
    return Response(status=201)


@app.route('/search', methods=['GET'])
def search_by_name():
    if 'forename' not in request.args or 'surname' not in request.args:
        logging.error('Forename or surname missing')
        return Response(status=400)

    forename = request.args['forename']
    surname = request.args['surname']

    search_type = app.config['SEARCH_TYPE']
    if 'type' in request.args:
        search_type = request.args['type']

    result = []
    if search_type == 'phonetic':
        result = phonetic_search(forename, surname)
    elif search_type == 'distance':
        result = distance_search(forename, surname)
    elif search_type == 'combined':
        result = combined_search(forename, surname)
    else:
        return Response(status=400)

    # TODO: process results...
    return Response(json.dumps(result), status=200, mimetype='application/json')
