__author__ = 'stephaneki'

from django.test import TestCase, Client
from django.contrib.auth.models import User


class ViewTestCase(TestCase):
    def test_is_reachable(self):
        resp = self.client.get("/home/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('auctions' in resp.context)
        self.assertEqual([auction.pk for auction in resp.context['auctions']], [1, 2, 3, 4])

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

    def test_user_with_no_account_cannot_signin(self):
        resp = self.client.post("/signin/", {'username': 'test', 'password': 'test'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['error'], "Wrong username or password ! ! !")


class SearchViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client = None

    def test_if_search_query_empty_result_empty(self):
        resp = self.client.get("/search/?q=")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["location"], "http://testserver/results/?page=1")
        error = self.client.session.get("search_error")
        self.assertEqual(error, "Nothing found in the database")

    def test_if_two_auctions_have_same_name_then_return_both(self):
        resp = self.client.get("/search/?q=Awsome+bike")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'], 'http://testserver/results/?page=1')
        # self.assertFalse(re.search("Stars wars bike 1", resp.content) is None)
        # self.assertFalse(re.search("Stars wars bike 2", resp.content) is None)


class EditAuctionTestCase(TestCase):
    pass


class RegistrationTestCase(TestCase):
    pass


class ChangePasswordTestCase(TestCase):
    pass


class SelectLanguageTestCase(TestCase):
    pass

















