__author__ = 'stephaneki'
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, Client

from yaasApp.models import Auction


class BanAuctionTestCase(TestCase):
    def setUp(self):
        self.administrator = User.objects.get(id=2)
        self.client = Client()

    def tearDown(self):
        self.administrator = None
        self.client = None

    def sign_in_first(self):
        return self.client.login(username=self.administrator.username, password="1")

    def test_only_administrator_can_ban(self):
        self.client.login(username="xx", password="xx")
        response = self.client.get('/banauction/4')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/signin/?next=/banauction/4")

    def test_user_redirected_to_home(self):
        self.sign_in_first()
        self.assertEqual(Auction.objects.get(id=1).state, 1)
        response = self.client.get('/banauction/1')
        self.assertEqual(Auction.objects.get(id=1).state, 2)
        self.assertRedirects(response, "/home/")

    def test_only_active_auction_can_be_banned(self):
        self.sign_in_first()
        self.assertEqual(Auction.objects.get(id=6).state, 4)  # Adjudicated
        response = self.client.get('/banauction/6')
        self.assertTemplateUsed(response, "auction.html")
        self.assertEqual(response.context['error'], 'You can only ban active auctions')

    def test_seller_and_all_bidders_are_notified(self):
        self.sign_in_first()
        self.client.get('/banauction/1')

        self.assertEqual(len(mail.outbox), Auction.objects.get(id=1).bid_set.count()+1)

        self.assertEqual(mail.outbox[0].to[0], Auction.objects.get(id=1).seller.email)
        self.assertEqual(mail.outbox[0].subject, 'Your auction <TOYOTA Carina> has been banned')

        self.assertEqual(mail.outbox[1].to[0], Auction.objects.get(id=1).last_bid().bidder.email)
        self.assertEqual(mail.outbox[1].subject, 'Auction <TOYOTA Carina> has been banned')
