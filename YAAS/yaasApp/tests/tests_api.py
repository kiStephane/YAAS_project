import base64

from rest_framework.renderers import JSONRenderer
from rest_framework.test import APITestCase

from yaasApp.models import Auction
from yaasApp.serializers import AuctionSerializer


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

    def test_return_all_auctions_if_no_query_string(self):
        response = self.client.get("/api/v1/search/")
        self.assertEqual(response.status_code, 200)
        auctions = Auction.objects.filter(state=1)
        expected = JSONRenderer().render(AuctionSerializer(auctions, many=True).data)
        self.assertJSONEqual(response.content, expected)


class BidApiTestCase(APITestCase):
    auth_headers_1 = {
        'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode('ski:1'),
    }

    auth_headers_2 = {
        'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode('ski2:1'),
    }

    def test_if_not_registered_then_cannot_bid(self):
        resp = self.client.post("/api/v1/createbid/1")
        self.assertEqual(resp.status_code, 401, "Unauthorized")

    def test_seller_cannot_bid_for_his_auction(self):
        resp = self.client.post("/api/v1/createbid/3", data={}, **self.auth_headers_1)
        self.assertEqual(resp.status_code, 403)
        expected = {'details': 'A seller cannot bid for his own auction'}
        self.assertJSONEqual(resp.content, expected)

    def test_cannot_bid_for_an_auction_that_does_not_exist(self):
        resp = self.client.post("/api/v1/createbid/10", **self.auth_headers_1)
        self.assertEqual(resp.status_code, 400, "Expected BAD REQUEST")
        self.assertEqual(resp.data, {'details': "The auction you want to bid for does not exist !"})

    def test_error_if_bid_under_last_bid(self):
        resp = self.client.post("/api/v1/createbid/1", {"price": 3000.0}, **self.auth_headers_2)
        self.assertEqual(resp.status_code, 403)  # Expected Forbidden
        self.assertEqual(resp.data, {'details': "Your bid must be greater than the last bid for this auction",
                                     'minimum_bid': 4000.01})

    def test_error_if_bidder_try_to_bid_already_winning_auction(self):
        resp = self.client.post("/api/v1/createbid/1", {"auction_id": 1, "price": 7000}, **self.auth_headers_1)
        self.assertEqual(resp.status_code, 403, "Cannot bid for already winning auction")
        self.assertEqual(resp.data, {'details': "Cannot bid for already winning auction"})
