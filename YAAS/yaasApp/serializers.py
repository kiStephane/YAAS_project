__author__ = 'stephaneki'
from rest_framework import serializers

from yaasApp.models import Auction


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ("id", "title", "creation_date", "description", "deadline", "seller", "minimum_price", "state")