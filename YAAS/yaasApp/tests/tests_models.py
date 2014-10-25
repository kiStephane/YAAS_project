"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import mock
from django.contrib.auth.models import User
from django.utils import timezone
import pytz

from yaasApp.models import Auction, Bid


class AuctionTestCase(TestCase):
    def setUp(self):
        self.my_auction = Auction.objects.get(id=1)

    def tearDown(self):
        self.my_auction = None

    def test_has_require_properties(self):
        self.assertEqual(self.my_auction.seller, User.objects.get(id=3), "The seller should be the one User 2")
        self.assertEqual(self.my_auction.title, "TOYOTA Carina", "My auction title should be <<TOYOTA Carina>>")
        self.assertEqual(self.my_auction.description, "This is a new car")
        self.assertEqual(self.my_auction.minimum_price, 2000)
        self.assertEqual(self.my_auction.deadline,
                         pytz.timezone("UTC").localize(
                             timezone.datetime(2014, 10, 24, 17, 10, 12)))  # 2014-10-25T17:10:12Z
        self.assertEqual(self.my_auction.creation_date,
                         pytz.timezone("UTC").localize(
                             timezone.datetime(2014, 10, 5, 16, 15, 32, 905000)))  # 2014-10-05T16:15:32.905Z

    def test_default_state_is_active(self):
        self.assertEqual(self.my_auction.state, 1)

    @mock.patch('django.utils.timezone.now')
    def test_is_due(self, my_mock):
        my_mock.return_value = pytz.timezone("UTC").localize(
            timezone.datetime(2014, 10, 20, 17, 10, 12))

        auction = Auction.objects.get(id=1)
        self.assertFalse(auction.is_due())


class BidTestCase(TestCase):
    def setUp(self):
        self.my_bid = Bid.objects.get(id=1)

    def tearDown(self):
        self.my_bid = None

    def test_has_require_properties(self):
        self.assertEqual(self.my_bid.bidder, User.objects.get(id=4), "The bidder is the user with id 4")
        self.assertEqual(self.my_bid.price, 4000, "The price for this bid is 4000")
        self.assertEqual(self.my_bid.auction, Auction.objects.get(id=1), "This bid is on auction 1")
        time = pytz.timezone("UTC").localize(timezone.datetime(2014, 10, 7))
        self.assertEqual(self.my_bid.time, time)

