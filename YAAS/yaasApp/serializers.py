__author__ = 'stephaneki'
from rest_framework import serializers

from yaasApp.models import Auction, Bid


class AuctionSerializer(serializers.ModelSerializer):
    seller = serializers.Field(source="seller.username")

    class Meta:
        model = Auction
        fields = ("id", "title", "creation_date", "description", "deadline", "seller", "minimum_price", "state")


class BidSerializer(serializers.ModelSerializer):
    auction = serializers.Field(source='auction.title')
    bidder = serializers.Field(source='bidder.username')

    class Meta:
        model = Bid
        fields = ("id", "auction", "bidder", "price", "time")