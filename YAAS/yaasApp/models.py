# Create your models here.

from django.db import models
from django.contrib.auth.models import User


class Auction(models.Model):
    title = models.CharField(max_length=30)
    creation_date = models.DateTimeField()
    description = models.CharField(max_length=500)
    deadline = models.DateTimeField()
    seller = models.ForeignKey(User)
    state = models.CharField(max_length=10, default='active')