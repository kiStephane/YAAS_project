import sys
from django.contrib.auth.models import User
from yaasApp.models import Auction

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
            auction = Auction.objects.get(title="dummy-auction"+str(j))
            auction.delete()
            user = User.objects.get(username="User"+str(j))
            user.delete()