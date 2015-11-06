from application import app
from flask import Response, request
from application.search import elastic, phonetic_search, distance_search, combined_search, \
    exact_search, get_for_title_number
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
        'dependencies': {}
    }

    es_response = requests.get(app.config['ELASTICSEARCH_URL'])
    if es_response.status_code == 200:
        status = 200
    else:
        status = 500
    result['dependencies']['elasticsearch'] = str(es_response.status_code) + ' ' + es_response.reason

    return Response(json.dumps(result), status=status, mimetype='application/json')


@app.route('/names', methods=['POST'])
def add_index_entry():
    if request.headers['Content-Type'] != "application/json":
        return Response(status=415)

    data = request.get_json(force=True)

    logging.info(data)

    # Step 1: get all the title numbers in this pack and isolate the unique ones
    title_numbers = []
    for item in data:
        title_number = item['title_number']
        if title_number not in title_numbers:
            title_numbers.append(title_number)

    # Step 2: for those title numbers, get related ES records and remove them
    es_records = []
    for title_number in title_numbers:
        logging.debug('Will un-index title number: %s', title_number)
        result = get_for_title_number(title_number)
        es_records += result

    # Step 2b: remove them
    for record in es_records:
        logging.debug('Delete id %s', record['_id'])
        elastic.delete(index='index', doc_type='names', id=record['_id'])

    # Step 3: index the new records
    for item in data:
        index_item = {
            'title_number': item['title_number'],
            'office': item['office'],
            'sub_register': item['sub_register'],
            'name_type': item['name_type']
        }

        if item['name_type'] == 'Private':
            index_item['forenames'] = " ".join(item['registered_proprietor']['forenames'])
            index_item['surname'] = item['registered_proprietor']['surname']
            index_item['full_name'] = item['registered_proprietor']['full_name']
        else:
            index_item['full_name'] = item['registered_proprietor']['full_name']

        result = elastic.index(index='index', doc_type='names', body=index_item)
        logging.info('Indexed with id %s', result['_id'])

    elastic.indices.refresh(index="index")
    return Response(status=201)


@app.route('/search', methods=['GET'])
def search_by_name():
    search_type = app.config['SEARCH_TYPE']
    if 'type' in request.args:
        search_type = request.args['type']

    surname = forename = name = ''

    if search_type in ['phonetic', 'distance', 'combined']:
        if 'forename' not in request.args or 'surname' not in request.args:
            logging.error('Forename or surname missing')
            return Response('Forename or surname missing', status=400)
        forename = request.args['forename']
        surname = request.args['surname']

    elif search_type == 'exact':
        if 'name' not in request.args:
            logging.error('Name is missing')
            return Response("Name not provided", status=400)
        name = request.args['name']

    else:
        logging.error('Invalid search type')
        return Response(status=400)

    if search_type == 'phonetic':
        result = phonetic_search(forename, surname)
    elif search_type == 'distance':
        result = distance_search(forename, surname)
    elif search_type == 'combined':
        result = combined_search(forename, surname)
    elif search_type == 'exact':
        result = exact_search(name)
    else:
        return Response('Invalid search type: ' + search_type, status=400)

    # TODO: process results...
    return Response(json.dumps(result), status=200, mimetype='application/json')
