import pytz

__author__ = 'stephaneki'

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.utils import timezone


class CreateBidViewTestCase(TestCase):
    def setUp(self):
        self.my_user = User.objects.get(id=4)
        self.client = Client()

    def tearDown(self):
        self.my_user = None
        self.client = None

    def sign_in_first(self):
        login_successful = self.client.login(username=self.my_user.username, password="1")
        self.assertTrue(login_successful)
        return login_successful

    def test_if_not_registered_then_cannot_bid(self):
        resp = self.client.get("/createbid/2")
        self.assertEqual(resp.status_code, 302, "The user is redirected because he is not logged in")
        self.assertEqual(resp['Location'], 'http://testserver/signin/?next=/createbid/2',
                         "The next url is /createbid/2")

    def test_cannot_bid_for_an_auction_that_does_not_exist(self):
        self.sign_in_first()
        resp = self.client.get("/createbid/10")
        self.assertEqual(resp.status_code, 302, "The user is redirected because the auction does not exist")
        self.assertEqual(resp['Location'], 'http://testserver/home/', "The next url is /home/")
        session_error = self.client.session.get("error_to_home")
        self.assertTrue(session_error == "The auction you want to bid for does not exist !")

    def test_seller_cannot_bid_for_his_own_auction(self):
        self.sign_in_first()
        resp = self.client.get("/createbid/3")
        self.assertEqual(resp.status_code, 302, "The user is redirected because he is the seller")
        self.assertEqual(resp['Location'], 'http://testserver/auction/3',
                         "The next url is /auction/3")
        session_error = self.client.session.get("error_to_auction_show")
        self.assertTrue(session_error == "You cannot bid because you are the seller !")

    def test_error_if_bid_under_minimum(self):
        self.sign_in_first()
        resp = self.client.post("/createbid/2", {"auction_id": 2,
                                                 "price": 300})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['error'] == "Not valid data")

    def test_bid_confirmation_should_contain_auction_description(self):
        self.assertTrue(False)

    def test_first_bid_should_be_greater_than_minimum_price(self):
        self.assertTrue(False)

    def test_error_if_bid_less_than_previous_bid(self):
        self.assertTrue(False)

    def test_error_if_bidder_try_to_bid_already_winning_auction(self):
        self.assertTrue(False)

    def test_seller_receive_email_if_new_bid_registered(self):
        self.assertTrue(False)

    def test_last_bidder_receive_email_if_new_bid_registered(self):
        self.assertTrue(False)

    def test_new_bidder_receive_email_on_bid_create(self):
        self.assertTrue(False)

    def test_extend_deadline_for_five_minute_if_last_bid_during_last_five_minutes(self):
        self.assertTrue(False)