import sys
from django.contrib.auth.models import User
from yaasApp.models import Auction, Bid

__author__ = 'stephaneki'
from django.core.management import BaseCommand


class Command(BaseCommand):
    args = '[count]'

    def handle(self, count=20, *args, **options):

        try:
            i = int(count)
        except ValueError:
            print u'n is to be a number!'
            sys.exit(1)

        for j in xrange(i):
            user = User(username="User" + str(j), password=str(j))
            user.save()
            auction = Auction(title="dummy-auction" + str(j),
                              creation_date="2014-10-24 10:10:10",
                              deadline="2014-10-29 10:10:10",
                              minimum_price="555.5", seller=user)
            auction.save()

        for k in xrange(i):
            if k % 2 == 0:
                if k != i:
                    bid = Bid(auction=Auction.objects.get(title="dummy-auction" + str(k+1)),
                              bidder=User.objects.get(username="User" + str(k)),
                              time="2014-10-27 10:10:10",
                              price="1000")
                    bid.save()