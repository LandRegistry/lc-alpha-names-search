from application import app
from flask import Response, request
from application.search import elastic, exact_search_full, get_for_title_number, exact_search_structured
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


@app.route('/proprietors', methods=['POST'])
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


@app.route('/proprietors', methods=['GET'])
def search_by_name():
    if 'forenames' in request.args and 'surname' in request.args:
        name = {
            'forenames': request.args['forenames'].split(' '),
            'surname': request.args['surname']
        }
        result = exact_search_structured(name)
    elif 'fullname' in request.args:
        name = request.args['fullname']
        result = exact_search_full(name)
    else:
        return Response('Either fullname or both forenames and surname must be provided', status=400)

    return Response(json.dumps(result), status=200, mimetype='application/json')
