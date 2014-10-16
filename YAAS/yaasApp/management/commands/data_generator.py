__author__ = 'stephaneki'
import sys
from django.contrib.auth.models import User
from datetime import timedelta
from django.core.management import BaseCommand
from django.utils import timezone
from yaasApp.models import Auction, Bid


class Command(BaseCommand):
    args = '[count]'

    def handle(self, count=50, *args, **options):
        try:
            i = int(count)
        except ValueError:
            print u'n is to be a number!'
            sys.exit(1)

        for j in xrange(i):
            user = User(username="User" + str(j), password=str(j))
            user.save()
            auction = Auction(title="dummy-auction" + str(j),
                              creation_date=timezone.now()+timedelta(days=-10),
                              deadline=timezone.now()+timedelta(hours=7),
                              minimum_price="555.5", seller=user)
            auction.save()
            if j % 2 != 0:
                if j != i:
                    bid = Bid(auction=Auction.objects.get(title="dummy-auction" + str(j - 1)),
                              bidder=User.objects.get(username="User" + str(j)),
                              time=timezone.now()+timedelta(days=-3),
                              price="1000")
                    bid.save()