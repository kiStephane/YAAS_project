__author__ = 'stephaneki'

from django.test import TestCase
from django.test.client import Client


class SearchApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client = None

    def test_api_only_handle_get_requests(self):
        response = self.client.put("/api/v1/search/")
        self.assertEqual(response.status_code, 405, 'METHOD NOT ALLOWED')

    def test_if_get_parameters_incorrect_raise_400_error(self):
        response = self.client.get("/api/v1/search/?query=Awsome")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"details": "The parameter keyword should be q"})

    def test_if_element_found_result_send_json_in_format(self):
        response = self.client.get("/api/v1/search/?q=Steeve")
        self.assertEqual(response.status_code, 200)
        expected = [{
            'description': 'This book does not exist',
            'title': 'Steeve Jobs - a robber',
            'minimum_price': 300.0,
            'creation_date': '2014-10-05T17:11:11.089Z',
            'state': 1,
            'deadline': '2014-10-25T17:10:12Z',
            'seller': 3,
            'id': 2
        }]
        self.assertJSONEqual(response.content, expected)


class BidApiTestCase(TestCase):
    pass
