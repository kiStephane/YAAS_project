# Create your models here.
from django.core.validators import MinValueValidator

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Auction(models.Model):
    title = models.CharField(max_length=30)
    creation_date = models.DateTimeField(default=datetime.now())
    description = models.CharField(max_length=500)
    deadline = models.DateTimeField()
    seller = models.ForeignKey(User)
    minimum_price = models.IntegerField(validators=[MinValueValidator(0)])
    state = models.CharField(max_length=10, default='active')