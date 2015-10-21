from application.routes import app
from unittest import mock
from application.search import search, phonetic_search, distance_search, combined_search
import json


# index_entry = '[{"office": "Willborough Office", "sub_register": "Proprietorship",' + \
#               '"registered_proprietor": "Kristoffer Demarco Koepp","name_type": "Standard",' + \
#               '"title_number": "FT80668"}]'

class FakeResponse(object):
    def __init__(self, status_code=200):
        super(FakeResponse, self).__init__()
        self.status_code = status_code
        self.reason = 'RS'

index_entry = '[{' \
              '    "name_type": "Private",' \
              '    "sub_register": "B",' \
              '    "office": "OFFICE",' \
              '    "title_number": "ZZ826242",' \
              '    "registered_proprietor": {' \
              '        "forenames": ["Tracey", "Alvina"],' \
              '        "full_name": "Tracey Alvina Johnston",' \
              '       "surname": "Johnston"' \
              '    }' \
              '}]'

returndata = {
    'hits': {
        'total': 1,
        'hits': [
            {
                '_score': 10,
                '_source': {
                    "forenames": "Tracey Alvina",
                    "name_type": "Private",
                    "sub_register": "B",
                    "surname": "Johnston",
                    "office": "OFFICE",
                    "title_number": "ZZ826242",
                    "full_name": "Tracey Alvina Johnston"
                }
            }
        ]
    }
}

# mock_es_search = {
#     'return_value': mock.Mock(**{
#         'elastic.return_value': returndata
#     })
# }

# mock_es_search = {
#     'return_value': mock.Mock(**{
#         'search.return_value': returndata
#     })
# }
mock_es_search = {
    'return_value': returndata
}

class TestWorking:
    def setup_method(self, method):
        self.app = app.test_client()

    def test_health_check(self):
        response = self.app.get("/")
        assert response.status_code == 200

    @mock.patch('application.routes.elastic')
    @mock.patch('requests.get', return_value=FakeResponse(status_code=200))
    @mock.patch('requests.put', return_value=FakeResponse(status_code=200))
    def test_healthcheck(self, mock_put, mock_get, mock_elastic):
        response = self.app.get('/health')
        assert response.status_code == 200


    @mock.patch('application.routes.elastic')
    @mock.patch('requests.get', return_value=FakeResponse(status_code=200))
    def test_add_index_entry(self, mock_get, mock_elastic):
        headers = {'Content-Type': 'application/json'}
        response = self.app.post('/names', data=index_entry, headers=headers)
        assert response.status_code == 201

        # Confirm that the ES APIs were called:
        name, args, kwargs = mock_elastic.method_calls[0]  # Call to index
        assert name == 'index'
        assert kwargs['body']['title_number'] == 'ZZ826242'

        name, args, kwargs = mock_elastic.method_calls[1]  # Call to indices
        assert name == 'indices.refresh'
        assert kwargs['index'] == 'index'

    @mock.patch('application.search.elastic.search')
    def test_phonetic_search(self, me):
        result = phonetic_search('Bob', 'Howard')
        query = me.call_args[1]['body']

        # Ensure phonetic query passed to ES...
        assert query['query']['bool']['must'][0]['match']['forenames.phonetic']['query'] == 'Bob'

    @mock.patch('application.search.elastic.search')
    def test_distance_search(self, me):
        result = distance_search('Robert', 'Howard')
        query = me.call_args[1]['body']

        # Ensure distance query passed to ES...
        assert query['query']['bool']['must'][0]['match']['forenames']['query'] == 'Robert'
        assert query['query']['bool']['must'][0]['match']['forenames']['fuzziness'] == '1'

    @mock.patch('application.search.elastic.search')
    def test_combined_search(self, me):
        result = combined_search('Robert', 'Howard')
        query = me.call_args[1]['body']
        print(query)
        # Ensure combined query passed to ES...
        must = query['query']['bool']['must']
        assert must[0]['bool']['should'][0]['match']['surname']['query'] == 'Howard'

    @mock.patch('application.search.elastic.search')
    def test_search_route_phonetic(self, es):
        self.app.get('/search?forename=Bob&surname=Howard&type=phonetic')
        query = es.call_args[1]['body']
        assert query['query']['bool']['must'][0]['match']['forenames.phonetic']['query'] == 'Bob'

    @mock.patch('application.search.elastic.search')
    def test_search_route_distance(self, es):
        self.app.get('/search?forename=Robert&surname=Howard&type=distance')
        query = es.call_args[1]['body']
        assert query['query']['bool']['must'][0]['match']['forenames']['query'] == 'Robert'
        assert query['query']['bool']['must'][0]['match']['forenames']['fuzziness'] == '1'

    @mock.patch('application.search.elastic.search')
    def test_search_route_combined(self, es):
        self.app.get('/search?forename=Bob&surname=Howard&type=combined')
        query = es.call_args[1]['body']
        must = query['query']['bool']['must']
        assert must[0]['bool']['should'][0]['match']['surname']['query'] == 'Howard'

    def test_search_route_name_missing(self):
        result = self.app.get('/search?forename=Bob')
        assert result.status_code == 400

    def test_search_route_invalid_type(self):
        result = self.app.get('/search?forename=Bob&surname=Howard&type=magical_mystery')
        assert result.status_code == 400

    @mock.patch('application.search.elastic.search', **mock_es_search)
    def test_search_call(self, me):
        d = search({'foo': 'bar'})
        assert len(d) == 1
        assert d[0]['title_number'] == 'ZZ826242'
