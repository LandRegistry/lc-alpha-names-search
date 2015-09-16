from application import app
from flask import Response, request
from elasticsearch import Elasticsearch
import logging
import json

elastic = Elasticsearch()


@app.route('/', methods=["GET"])
def index():
    return Response(status=200)


@app.route('/entry', methods=['POST'])
def add_index_entry():
    if request.headers['Content-Type'] != "application/json":
        return Response(status=415)

    data = request.get_json(force=True)
    logging.info(data)

    for item in data:
        result = elastic.index(index='index', doc_type='names', body=item)
        logging.info(result['created'])
    elastic.indices.refresh(index="index")
    return Response(status=201)


@app.route('/index', methods=['GET'])
def get_all():
    result = elastic.search(index='index', body={'query': {'match_all': {}}})

    logging.info("Got %d hits", result['hits']['total'])
    logging.info(result)

    return_data = []
    for hit in result['hits']['hits']:
        return_data.append(hit['_source'])

    return Response(json.dumps(return_data), status=200, mimetype='application/json')
