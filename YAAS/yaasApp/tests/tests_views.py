__author__ = 'stephaneki'

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client


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


class CreateAuctionViewTestCase(TestCase):
    my_user = None

    def setUp(self):
        self.my_user = User.objects.get(id=3)
        self.client = Client()

    def tearDown(self):
        self.my_user = None

    def test_creation_from_is_not_reachable_if_not_signed_in(self):
        resp = self.client.get("/createauction/")
        self.assertEqual(resp.status_code, 302, "The user is redirected because he is not logged in")
        self.assertEqual(resp['Location'], 'http://testserver/signin/?next=/createauction/')

    def test_if_user_logged_in_then_creation_form_sent(self):
        login_successful = self.client.login(username=self.my_user.username, password="xx")
        self.assertTrue(self.my_user.is_authenticated())
        self.assertTrue(login_successful)
        response = self.client.get("/createauction/")
        self.assertTemplateUsed(response, 'createauction.html')

    def test_the_minimum_price_should_be_positive(self):
        self.assertTrue(False)

    def test_if_deadline_under_72_hours_after_creation_then_form_not_valid(self):
        self.assertTrue(False)







