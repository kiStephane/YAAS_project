"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from yaasApp.models import Auction
from datetime import datetime
from django.contrib.auth.models import User


class AuctionTestCase(TestCase):
    my_auction = None
    seller = None

    def setUp(self):
        self.seller = User.objects.create(username='test', password='test')
        self.my_auction = Auction.objects.create(id=0, seller=self.seller, creation_date=datetime(2014, 10, 1),
                                                 deadline=datetime(2014, 10, 4))
        self.my_auction.title = "Car"
        self.my_auction.description = "Description of my car"
        self.my_auction.minimum_price = 3000

    def tearDown(self):
        pass

    def test_has_require_properties(self):
        self.assertEqual(self.my_auction.seller, self.seller, "The seller should be the one specified before")
        self.assertEqual(self.my_auction.title, "Car", "My auction title should be <<Car>>")
        self.assertEqual(self.my_auction.description, "Description of my car")
        self.assertEqual(self.my_auction.minimum_price, 3000)
        self.assertEqual(self.my_auction.deadline, datetime(2014, 10, 4))
        self.assertEqual(self.my_auction.creation_date, datetime(2014, 10, 1),
                         "My auction creation date should be 01/10/2014")

    def test_default_state_is_active(self):
        self.assertEqual(self.my_auction.state, 'active')
