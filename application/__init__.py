from flask import Flask
import os
from log.logger import setup_logging
import requests
import json
import logging


metaphone = {
    "settings": {
        "analysis": {
            "filter": {
                "dbl_metaphone": {
                    "type": "phonetic",
                    "encoder": "double_metaphone"
                }
            },
            "analyzer": {
                "dbl_metaphone": {
                    "tokenizer": "standard",
                    "filter": "dbl_metaphone"
                }
            }
        }
    }
}

# maps some fields...
mapping = {
    "properties": {
        "surname": {
            "type": "string",
            "fields": {
                "phonetic": {
                    "type": "string",
                    "analyzer": "dbl_metaphone"
                }
            }
        },
        "forenames": {
            "type": "string",
            "fields": {
                "phonetic": {
                    "type": "string",
                    "analyzer": "dbl_metaphone"
                }
            }
        }
    }
}

app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))

setup_logging(app.config['DEBUG'])

response = requests.get("http://localhost:9200/index/_mapping/names")
if response.status_code == 404:
    resp = requests.put("http://localhost:9200/index", data=json.dumps(metaphone), headers={'Content-Type': 'application/json'})
    logging.info('Add Filters: ' + resp.status_code)
    resp = requests.put("http://localhost:9200/index/_mapping/names", data=json.dumps(mapping), headers={'Content-Type': 'application/json'})
    logging.info('Map Fields: ' + resp.status_code)
else:
    logging.info('Mappings already exist')
