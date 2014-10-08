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












