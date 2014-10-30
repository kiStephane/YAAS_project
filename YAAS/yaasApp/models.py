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
        # 3: 'due',
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

    class Meta:
        permissions = (
            ("can_ban", "Can ban auction"),
        )

    def get_state_label(self):
        return self.state_label[self.state]

    def is_due(self):
        return timezone.now() > self.deadline

    def ban(self):
        if self.state is 1:
            self.state = 2
            return True
        return False

    def last_bid(self):
        bids = self.bid_set.all()
        last = None
        for bid in bids:
            if last is None:
                last = bid
            elif last.price < bid.price:
                last = bid
        return last

    def last_bid_price(self):
        last = self.last_bid()
        return last.price if last else None

    def last_bidder_username(self):
        last = self.last_bid()
        return last.bidder.username if last else None

    def minimum_bid_price(self):
        return self.last_bid_price() + MINIMUM_BID_AUGMENTATION if self.last_bid_price() \
            else self.minimum_price + MINIMUM_BID_AUGMENTATION


class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    price = models.FloatField()
    bidder = models.ForeignKey(User)
    time = models.DateTimeField(default=timezone.now())
