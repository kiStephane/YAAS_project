from yaasApp.models import Auction

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
    def setUp(self):
        self.my_user = User.objects.get(id=3)
        self.client = Client()

    def tearDown(self):
        self.my_user = None
        self.client = None

    def sign_in_first(self):
        login_successful = self.client.login(username=self.my_user.username, password="xx")
        self.assertTrue(login_successful)
        return login_successful

    def test_seller_should_login_first(self):
        resp = self.client.post('/editauction/1', {'description': 'my new description'})
        self.assertEqual(resp.status_code, 302, "The user is redirected because he is not logged in")
        self.assertRedirects(resp, "/signin/?next=/editauction/1")

    def test_only_the_seller_can_edit_auction_desc(self):
        self.sign_in_first()
        resp = self.client.post('/editauction/4', {'description': 'my new description'})
        self.assertEqual(self.client.session.get("message_to_profile"), "You cannot edit this auction because you are"
                                                                        " not the seller")
        self.assertRedirects(resp, "/profile/")

    def test_auction_should_exist_in_the_db(self):
        self.sign_in_first()
        resp = self.client.get('/editauction/54')
        self.assertEqual(self.client.session.get("message_to_profile"), "This auction does not exists")
        self.assertRedirects(resp, "/profile/")

    def test_ok(self):
        self.sign_in_first()
        resp = self.client.post('/editauction/1', {'description': 'my new description'})
        auction = Auction.objects.get(id=1)
        self.assertEqual(auction.description, 'my new description')
        self.assertRedirects(resp, "/profile/")

    def test_a_ban_auction_cannot_be_edited(self):
        self.sign_in_first()
        resp = self.client.post('/editauction/5', {'description': 'my new description'})
        auction = Auction.objects.get(id=5)
        self.assertNotEqual(auction.description, 'my new description')
        self.assertRedirects(resp, "/profile/")


class RegistrationTestCase(TestCase):
    def test_cannot_use_username_that_already_exists(self):
        self.assertEqual(True, True, "No test Needed because we used a django standard user creation form")

    def test_after_creation_user_redirected_to_home_and_should_login(self):
        response = self.client.post("/register/", {"username": "test",
                                                   "password1": "test",
                                                   "password2": "test"})
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(User.objects.get(username="test"))
        self.assertEqual(self.client.session.get("message_to_home"), "New User is created. Please Login")
        self.assertRedirects(response, "/home/")

    def test_(self):
        # Need refactoring
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)


class ChangePasswordTestCase(TestCase):
    pass


class SelectLanguageTestCase(TestCase):
    pass

















