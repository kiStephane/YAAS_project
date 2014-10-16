__author__ = 'stephaneki'
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client

from yaasApp.models import Auction


class CreateAuctionViewTestCase(TestCase):
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

    def test_creation_from_is_not_reachable_if_not_signed_in(self):
        resp = self.client.get("/createauction/")
        self.assertEqual(resp.status_code, 302, "The user is redirected because he is not logged in")
        self.assertRedirects(resp, "/signin/?next=/createauction/")

    def test_after_signed_in_user_redirected_to_creation_form(self):
        resp = self.client.post("/signin/?next=/createauction/", {"username": self.my_user.username,
                                                                  "password": "xx"})
        self.assertEqual(resp.status_code, 302, "The user is redirected")
        self.assertEqual(resp['Location'], 'http://testserver/createauction/')
        self.assertRedirects(resp, "/createauction/")

    def test_if_user_logged_in_then_creation_form_sent(self):
        login_successful = self.sign_in_first()
        self.assertTrue(self.my_user.is_authenticated())
        self.assertTrue(login_successful)
        response = self.client.get("/createauction/")
        self.assertTemplateUsed(response, 'createauction.html')

    def test_the_minimum_price_should_be_positive(self):
        self.sign_in_first()
        resp = self.client.post("/createauction/", {"title": "New auction",
                                                    "description": "Auction description",
                                                    "creation_date": "10/10/14",
                                                    "deadline": "10/20/14",
                                                    "minimum_price": -100})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'minimum_price', "Ensure this value is greater than or equal to 0.")

    def test_if_deadline_under_72_hours_after_creation_then_form_not_valid(self):
        self.sign_in_first()
        resp = self.client.post("/createauction/", {"title": "New auction",
                                                    "description": "Auction description",
                                                    "creation_date": "10/10/14",
                                                    "deadline": "10/10/14",
                                                    "minimum_price": 100})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'deadline', "Deadline should be at least 72h after creation.")

        resp = self.client.post("/createauction/", {"title": "New auction",
                                                    "description": "Auction description",
                                                    "creation_date": "10/10/14",
                                                    "deadline": "10/13/14",
                                                    "minimum_price": 100})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "confirmation.html", "The data is valid then the user should confirm or not")

    def test_send_confirmation_if_post_data_valid(self):
        self.sign_in_first()
        resp = self.client.post("/createauction/", {"title": "New auction",
                                                    "description": "Auction description",
                                                    "creation_date": "10/10/14",
                                                    "deadline": "10/13/14",
                                                    "minimum_price": 100})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'confirmation.html')

    def test_if_user_select_yes_then_create_auction(self):
        self.test_send_confirmation_if_post_data_valid()
        resp = self.client.post("/saveauction/", {"option": 'Yes'})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'done.html')
        new_auction = Auction.objects.get(title="New auction")
        self.assertIsNot(new_auction, None)
        self.assertEqual(new_auction.description, "Auction description")

    def test_if_user_select_no_auction_not_created(self):
        self.test_send_confirmation_if_post_data_valid()
        resp = self.client.post("/saveauction/", {"option": 'No'})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'createauction.html')
        auctions = Auction.objects.filter(title="New auction")
        self.assertEqual(len(auctions), 0, "The object has does not exit in the database ")
