# Create your models here.
from django.core.validators import MinValueValidator

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Auction(models.Model):
    title = models.CharField(max_length=30)
    creation_date = models.DateTimeField(default=timezone.now())
    description = models.CharField(max_length=500)
    deadline = models.DateTimeField()
    seller = models.ForeignKey(User)
    minimum_price = models.FloatField(validators=[MinValueValidator(0)])
    state = models.CharField(max_length=10, default='active')


class Bid(models.Model):
    pass