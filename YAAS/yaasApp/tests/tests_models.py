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

    def setUp(self):
        self.my_auction = Auction.objects.get(id=1)

    def tearDown(self):
        self.my_auction = None

    def test_has_require_properties(self):
        self.assertEqual(self.my_auction.seller, User.objects.get(id=3), "The seller should be the one User 2")
        self.assertEqual(self.my_auction.title, "TOYOTA Carina", "My auction title should be <<TOYOTA Carina>>")
        self.assertEqual(self.my_auction.description, "This is a new car")
        self.assertEqual(self.my_auction.minimum_price, 2000)
        # self.assertEqual(self.my_auction.deadline, datetime(2014, 10, 25, 17, 10, 12))  # 2014-10-25T17:10:12Z
        # self.assertEqual(self.my_auction.creation_date, datetime(2014, 10, 5, 16, 15, 32.905),  # 2014-10-05T16:15:32.905Z
        # "My auction creation date should be 01/10/2014")

    def test_default_state_is_active(self):
        self.assertEqual(self.my_auction.state, 'active')
