from application.routes import app
from unittest import mock
import json


index_entry = '[{"office": "Willborough Office", "sub_register": "Proprietorship",' + \
              '"registered_proprietor": "Kristoffer Demarco Koepp","name_type": "Standard",' + \
              '"title_number": "FT80668"}]'

returndata = {
    'hits': {
        'total': 1,
        'hits': [
            {
                '_source': {
                    "office": "Willborough Office",
                    "sub_register": "Proprietorship",
                    "registered_proprietor": "Kristoffer Demarco Koepp",
                    "name_type": "Standard",
                    "title_number": "FT80668"
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
    def test_add_index_entry(self, mock_elastic):
        headers = {'Content-Type': 'application/json'}
        response = self.app.post('/entry', data=index_entry, headers=headers)
        assert response.status_code == 201

        # Confirm that the ES APIs were called:
        name, args, kwargs = mock_elastic.method_calls[0]  # Call to index
        assert name == 'index'
        assert kwargs['body']['title_number'] == 'FT80668'

        name, args, kwargs = mock_elastic.method_calls[1]  # Call to indices
        assert name == 'indices.refresh'
        assert kwargs['index'] == 'index'

    @mock.patch('application.routes.elastic.search', return_value=returndata)
    def test_retrieve_data(self, mock_elastic):
        response = self.app.get('/index')
        data = json.loads(response.data.decode('utf-8'))
        assert len(data) == 1
        assert data[0]['title_number'] == "FT80668"
