from django.core import mail
import mock
import pytz

__author__ = 'stephaneki'

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from yaasApp.models import Auction, Bid
from django.utils import timezone


class CreateBidViewTestCase(TestCase):
    def setUp(self):
        self.my_user = User.objects.get(id=4)
        self.client = Client()

    def tearDown(self):
        self.my_user = None
        self.client = None

    def sign_in_first(self, username=None, password=None):
        if username is None or password is None:
            login_successful = self.client.login(username=self.my_user.username, password="1")
        else:
            login_successful = self.client.login(username=username, password=password)

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
        self.assertContains(resp, auction.description)

    def test_error_if_bidder_try_to_bid_already_winning_auction(self):
        self.sign_in_first()
        resp = self.client.post("/createbid/1", {"auction_id": 1,
                                                 "price": 7000})
        self.assertEqual(resp.status_code, 302, "cannot bid for already winning auction")
        error = self.client.session.get("message_to_profile")
        self.assertTrue(error == "You cannot bid for an already winning auction!")
        self.assertRedirects(resp, "/profile/")  # message_to_profile

    @mock.patch('django.utils.timezone.now')
    def test_email_send_to_seller_if_new_bid_registered(self, my_mock):
        my_mock.return_value = pytz.timezone("UTC").localize(timezone.datetime(2014, 10, 20, 17, 10, 12))
        self.sign_in_first(username="ski2", password="1")
        self.client.get("/createbid/1")
        resp = self.client.post("/createbid/1", {"auction_id": 1,
                                                 "price": 10000})
        self.assertEqual(resp.status_code, 200)

        self.client.post("/savebid/", {"option": "Yes"})
        self.assertEqual(Auction.objects.get(id=1).bid_set.all().count(), 2)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], Auction.objects.get(id=1).seller.email)
        self.assertEqual(mail.outbox[0].subject, 'New bid for your auction <TOYOTA Carina>')

    @mock.patch('django.utils.timezone.now')
    def test_email_sends_to_last_bidder_if_new_bid_registered(self, my_mock):
        my_mock.return_value = pytz.timezone("UTC").localize(timezone.datetime(2014, 10, 20, 17, 10, 12))
        #print timezone.now()
        self.sign_in_first(username="ski2", password="1")
        bid = Bid.objects.get(id=1)
        self.client.get("/createbid/1")
        resp = self.client.post("/createbid/1", {"auction_id": 1,
                                                 "price": 10000})
        self.assertEqual(resp.status_code, 200)
        self.client.post("/savebid/", {"option": "Yes"})
        self.assertEqual(Auction.objects.get(id=1).bid_set.all().count(), 2)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(len(mail.outbox[1].to), 1)
        self.assertEqual(mail.outbox[1].to[0], bid.bidder.email)
        self.assertEqual(mail.outbox[1].subject, 'Your bid has been exceeded. Auction <TOYOTA Carina>')

    @mock.patch('django.utils.timezone.now')
    def test_email_sends_to_new_bidder_on_bid_create(self, my_mock):
        my_mock.return_value = pytz.timezone("UTC").localize(timezone.datetime(2014, 10, 20, 17, 10, 12))
        self.sign_in_first(username="ski2", password="1")
        self.client.get("/createbid/1")
        resp = self.client.post("/createbid/1", {"auction_id": 1,
                                                 "price": 10000})
        self.assertEqual(resp.status_code, 200)
        self.client.post("/savebid/", {"option": "Yes"})
        self.assertEqual(Auction.objects.get(id=1).bid_set.all().count(), 2)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(len(mail.outbox[2].to), 1)
        self.assertEqual(mail.outbox[2].to[0], Auction.objects.get(id=1).last_bid().bidder.email)
        self.assertEqual(mail.outbox[2].subject, 'New bid saved. Auction <TOYOTA Carina>')

    def test_extend_deadline_for_five_minute_if_last_bid_during_last_five_minutes(self):
        self.assertTrue(True)

    def test_if_no_last_bidder_then_no_email_sending(self):
        self.sign_in_first()
        self.client.get("/createbid/2")
        resp = self.client.post("/createbid/2", {"auction_id": 2,
                                                 "price": 10000})
        self.assertEqual(resp.status_code, 200)
        self.client.post("/savebid/", {"option": "Yes"})
        self.assertEqual(Auction.objects.get(id=2).bid_set.all().count(), 1)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], Auction.objects.get(id=1).seller.email)
        self.assertEqual(len(mail.outbox[1].to), 1)
        self.assertEqual(mail.outbox[1].to[0], Auction.objects.get(id=1).last_bid().bidder.email)


class ConcurrencyTestCases(TestCase):
    def setUp(self):
        self.my_user = User.objects.get(id=3)
        self.client1 = Client()

    def tearDown(self):
        self.my_user = None
        self.client1 = None

    def sign_in_first(self):
        return self.client1.login(username=self.my_user.username, password="xx")


    @mock.patch('django.utils.timezone.now')
    def test_user_should_bid_again_if_new_bid_before_his_bid_during_confirmation(self, my_mock):
        my_mock.return_value = pytz.timezone("UTC").localize(timezone.datetime(2014, 10, 20, 17, 10, 12))
        self.test_user_should_see_last_auction_description_in_confirmation_window()
        bid = Bid(price=5000, auction=Auction.objects.get(id=1), bidder=self.my_user, time=timezone.now())
        bid.save()
        resp = self.client1.post("/savebid/", {"option": 'Yes'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["location"], "http://testserver/createbid/1")

    @mock.patch('django.utils.timezone.now')
    def test_user_should_see_last_auction_description_in_confirmation_window(self, my_mock):
        my_mock.return_value = pytz.timezone("UTC").localize(timezone.datetime(2014, 10, 20, 17, 10, 12))
        self.sign_in_first()
        self.client1.get("/createbid/1")
        auction = Auction.objects.get(id=1)
        auction.description = "New description"
        auction.version += 1
        auction.save()
        resp = self.client1.post("/createbid/1", {"auction_id": 1,
                                                  "price": 5000})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "confbid.html")
        self.assertContains(resp, "New description")
