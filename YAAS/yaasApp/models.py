# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class Auction(models.Model):
    creation_date = models.DateField()
    author = models.ForeignKey(User)