from django.core import serializers
from yaasApp.models import Auction

__author__ = 'stephaneki'

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client


class SearchApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client = None

    def test_(self):  # TODO Rename the test
        auctions = Auction.objects.get(id=2)
        result = serializers.serialize("json", [auctions])

        resp = self.client.get("/api/search/2")
        self.assertEqual(resp.content, result)

    def test_bad_request(self):  # TODO Rename the test
        resp = self.client.get("/api/search/42")
        self.assertEqual(resp.status_code, 404)
