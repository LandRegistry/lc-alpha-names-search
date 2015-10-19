from application.routes import app
from unittest import mock
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


class TestWorking:
    def setup_method(self, method):
        self.app = app.test_client()

    def test_health_check(self):
        response = self.app.get("/")
        assert response.status_code == 200

    @mock.patch('application.routes.elastic')
    @mock.patch('requests.get', return_value=FakeResponse(status_code=404))
    @mock.patch('requests.put', return_value=FakeResponse(status_code=200))
    def test_healthcheck(self, mock_put, mock_get, mock_elastic):
        response = self.app.get('/health')

        print(dir(mock_get))
        print(mock_get.call_count)
        print(mock_put.call_count)
        print(mock_elastic)
        print(response.data)
        assert False


    # @mock.patch('application.routes.elastic')
    # @mock.patch('requests.get', return_value=FakeResponse(status_code=200))
    # def test_add_index_entry(self, mock_get, mock_elastic):
    #     headers = {'Content-Type': 'application/json'}
    #     response = self.app.post('/names', data=index_entry, headers=headers)
    #     assert response.status_code == 201
    #
    #     # Confirm that the ES APIs were called:
    #     print(mock_elastic.method_calls)
    #     print(mock_get.method_calls)
    #     name, args, kwargs = mock_elastic.method_calls[0]  # Call to index
    #     assert name == 'index'
    #     assert kwargs['body']['title_number'] == 'ZZ826242'
    #
    #     name, args, kwargs = mock_elastic.method_calls[1]  # Call to indices
    #     assert name == 'indices.refresh'
    #     assert kwargs['index'] == 'index'
    #     assert False