__author__ = 'stephaneki'

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
import re
from yaasApp.models import Auction, Bid
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
        self.assertRedirects(resp, "/signin/?next=/createbid/2")

    def test_cannot_bid_for_an_auction_that_does_not_exist(self):
        self.sign_in_first()
        resp = self.client.get("/createbid/10")
        self.assertEqual(resp.status_code, 302, "The user is redirected because the auction does not exist")
        session_error = self.client.session.get("error_to_home")
        self.assertTrue(session_error == "The auction you want to bid for does not exist !")
        self.assertRedirects(resp, "/home/")

    def test_seller_cannot_bid_for_his_own_auction(self):
        self.sign_in_first()
        resp = self.client.get("/createbid/3")
        self.assertEqual(resp.status_code, 302, "The user is redirected because he is the seller")
        session_error = self.client.session.get("error_to_auction_show")
        self.assertTrue(session_error == "You cannot bid because you are the seller !")
        self.assertRedirects(resp, "/auction/3")

    def test_error_if_bid_under_last_bid(self):
        self.sign_in_first()
        resp = self.client.post("/createbid/1", {"auction_id": 1,
                                                 "price": 3000})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['error'] == "Not valid data")

    def test_first_bid_should_be_greater_than_minimum_price(self):
        self.sign_in_first()
        resp = self.client.post("/createbid/2", {"auction_id": 2,
                                                 "price": 300})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['error'] == "Not valid data")

    def test_bid_confirmation_should_contain_auction_description(self):
        self.sign_in_first()
        resp = self.client.post("/createbid/2", {"auction_id": 2,
                                                 "price": 5000})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'confbid.html')
        auction = Auction.objects.filter(id=2)[0]
        self.assertFalse(re.search(auction.description, resp.content) is None)

    def test_error_if_bidder_try_to_bid_already_winning_auction(self):
        self.assertTrue(False)

    def test_mail_send_to_seller_if_new_bid_registered(self):
        self.assertTrue(False)

    def test_email_sends_to_last_bidder_if_new_bid_registered(self):
        self.assertTrue(False)

    def test_email_sends_to_new_bidder_on_bid_create(self):
        self.assertTrue(False)

    def test_extend_deadline_for_five_minute_if_last_bid_during_last_five_minutes(self):
        self.assertTrue(True)


class ConcurrencyTestCases(TestCase):
    def setUp(self):
        self.my_user1 = User.objects.get(id=4)
        self.my_user2 = User.objects.get(id=3)
        self.client1 = Client()
        self.client2 = Client()

    def tearDown(self):
        self.my_user1 = None
        self.my_user2 = None
        self.client2 = None
        self.client1 = None

    def sign_in_first(self):
        login_successful = self.client1.login(username=self.my_user1.username, password="1")
        self.assertTrue(login_successful)
        return login_successful

    def test_user_should_bid_again_if_new_bid_before_his_bid_during_confirmation(self):
        self.test_user_should_see_last_auction_description_in_confirmation_window()
        bid = Bid(price=5000, auction=Auction.objects.get(id=1), bidder=self.my_user1, time=timezone.now())
        bid.save()
        resp = self.client1.post("/savebid/", {"option": 'Yes'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["location"], "http://testserver/createbid/1")
        self.assertRedirects(resp, "/createbid/1")

    def test_user_should_see_last_auction_description_in_confirmation_window(self):
        self.sign_in_first()
        self.client1.get("/createbid/1")
        auction = Auction.objects.get(id=1)
        auction.description = "New description"
        auction.version += 1
        auction.save()
        resp = self.client1.post("/createbid/1", {"auction_id": 1,
                                                  "price": 5000})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'confbid.html')
        self.assertContains(resp, "New description")
