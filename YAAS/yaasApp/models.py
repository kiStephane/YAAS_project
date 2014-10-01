# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class Auction(models.Model):
    title = models.CharField(max_length=30)
    creation_date = models.DateField()
    seller = models.ForeignKey(User)