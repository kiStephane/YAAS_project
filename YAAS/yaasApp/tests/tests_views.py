__author__ = 'stephaneki'

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from yaasApp.models import Auction


class ViewTestCase(TestCase):
    def test_is_reachable(self):
        resp = self.client.get("/home/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('auctions' in resp.context)
        self.assertEqual([auction.pk for auction in resp.context['auctions']], [1, 2])

    def test_auction_is_well_fetch(self):
        resp = self.client.get("/auction/1")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('auction' in resp.context)
        self.assertEqual(resp.context['auction'].pk, 1)


class SignInViewTestCase(TestCase):
    def test_sign_in_form_is_reachable(self):
        resp = self.client.get("/signin/")
        self.assertEqual(resp.status_code, 200)

    def test_client_can_sign_in(self):
        user = User.objects.get(id=3)
        resp = self.client.post("/signin/", {'username': user.username, 'password': user.password})
        self.assertEqual(resp.status_code, 200)
        # self.assertEqual(resp['Location'], 'http://testserver/profile/')

    def test_user_with_no_account_cannot_signin(self):
        resp = self.client.post("/signin/", {'username': 'test', 'password': 'test'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['error'], "Wrong username or password ! ! !")


class BidForAnAuctionViewTestCase(TestCase):

    def test_if_not_registered_then_cannot_bid(self):
        self.assertTrue(False)

    def test_seller_cannot_on_his_own_auction(self):
        self.assertTrue(False)

    def test_error_if_bid_under_minimum(self):
        self.assertTrue(False)

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











