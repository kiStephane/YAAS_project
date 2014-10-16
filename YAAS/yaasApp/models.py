# Create your models here.
from django.core.validators import MinValueValidator

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

MINIMUM_BID_AUGMENTATION = 0.01


class Auction(models.Model):
    state_label = {
        1: 'active',
        2: 'ban',
        3: 'due',
        4: 'adjudicated'
    }
    title = models.CharField(max_length=30)
    creation_date = models.DateTimeField(default=timezone.now())
    description = models.CharField(max_length=500)
    deadline = models.DateTimeField()
    seller = models.ForeignKey(User)
    minimum_price = models.FloatField(validators=[MinValueValidator(0)])
    state = models.IntegerField(max_length=10, default=1)
    version = models.IntegerField(default=0)

    '''def get_state(self):
        return self._state

    def set_state(self, state):
        self._state = state

    state = property(get_state, set_state)'''

    def ban(self):
        if self.state is 1:
            self.state = 2
            return True
        return False

    def last_bid(self):
        bids = self.bid_set.all()
        if bids.count() == 0:
            return None
        else:
            last = None
            for bid in bids:
                if last is None:
                    last = bid
                elif last.price < bid.price:
                    last = bid
            return last

    def last_bid_price(self):
        last = self.last_bid()
        if last:
            return last.price
        else:
            return None

    def last_bidder_username(self):
        last = self.last_bid()
        if last:
            return last.bidder.username
        else:
            return None

    def minimum_bid_price(self):
        if self.last_bid_price() is None:
            return self.minimum_price + MINIMUM_BID_AUGMENTATION

        return self.last_bid_price() + MINIMUM_BID_AUGMENTATION

    def get_winner(self):

        pass


class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    price = models.FloatField()
    bidder = models.ForeignKey(User)
    time = models.DateTimeField(default=timezone.now())
