from application import app
from flask import Response, request
from application.search import elastic, phonetic_search, distance_search, combined_search
import logging
import json




@app.route('/', methods=["GET"])
def index():
    return Response(status=200)


@app.route('/names', methods=['POST'])
def add_index_entry():
    if request.headers['Content-Type'] != "application/json":
        return Response(status=415)

    data = request.get_json(force=True)
    # Data structure coming in isn't quite how we want to index it...
    index_item = {
        'title_number': data['title_number'],
        'office': data['office'],
        'sub_register': data['sub_register'],
        'name_type': data['name_type']
    }

    if data['name_type'] == 'Private':
        index_item['forenames'] = " ".join(data['registered_proprietor']['forenames'])
        index_item['surname'] = data['registered_proprietor']['surname']
        index_item['full_name'] = index_item['forenames'] + ' ' + index_item['surname']
    else:  # Bankruptcies can't be against companies, etc.
        return Response(status=501)

    logging.info(data)

    for item in data:
        result = elastic.index(index='index', doc_type='names', body=item)
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



# @app.route('/index', methods=['GET'])
# def get_all():
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
