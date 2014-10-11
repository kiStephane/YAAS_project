# Create your models here.
from django.core.validators import MinValueValidator

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def is_active():
    return True


class Auction(models.Model):
    title = models.CharField(max_length=30)
    creation_date = models.DateTimeField(default=timezone.now())
    description = models.CharField(max_length=500)
    deadline = models.DateTimeField()
    seller = models.ForeignKey(User)
    minimum_price = models.FloatField(validators=[MinValueValidator(0)])
    state = models.CharField(max_length=10, default='active')
    version = models.IntegerField(default=0)

    def _get_state(self):
        """Returns the current state of the auction """
        return 'active'

    def last_bid_price(self):
        bids = self.bid_set.all()
        if bids.count() == 0:
            return self.minimum_price
        else:
            last = None
            for bid in bids:
                if last is None:
                    last = bid
                elif last.price < bid.price:
                    last = bid
        return last.price


class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    price = models.FloatField()
    bidder = models.ForeignKey(User)
    time = models.DateTimeField(default=timezone.now())
