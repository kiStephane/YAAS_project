__author__ = 'stephaneki'
import json

from django.utils import timezone
from rest_framework.decorators import authentication_classes, permission_classes, renderer_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import *

from yaasApp.views import send_mail_to_seller, send_mail_to_last_bid_before_new_one, send_mail_to_bidder
from yaasApp.models import Auction, Bid
from yaasApp.search import get_query
from yaasApp.serializers import AuctionSerializer, BidSerializer


@api_view(['GET'])
@renderer_classes([JSONRenderer, ])
def auction_search_api(request):
    result_data = {}
    if 'q' in request.GET:
        query_string = request.GET["q"]
        entry_query = get_query(query_string, ['title'])
        if entry_query:
            found_entries = Auction.objects.filter(entry_query)
            auctions = found_entries
            result_data = AuctionSerializer(auctions, many=True).data

        return Response(result_data)
    elif not len(request.GET) is 0:
        return Response({"details": "The parameter keyword should be q"}, status=400)
    else:
        auctions = Auction.objects.filter(state=1)
        result_data = AuctionSerializer(auctions, many=True).data
        return Response(result_data)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def bid_api(request, pk):
    auction = Auction.objects.filter(id=pk).filter(state=1)
    if auction.count() is 0:
        # An auction with this id does not exist in our database
        response = Response({'details': 'The auction you want to bid for does not exist !'}, status=400)
    else:
        if auction[0].seller.username == request.user.username:
            # a seller cannot bid for his own auction
            response = Response({'details': 'A seller cannot bid for his own auction'}, status=403)
        elif auction[0].last_bidder_username() == request.user.username:
            # a bidder cannot bid an already winning auction
            response = Response({'details': "Cannot bid for already winning auction"}, status=403)
        else:
            if 'price' in request.POST:
                price = json.loads(request.POST.get('price'))
                minimum_price = auction[0].minimum_bid_price()
                if minimum_price > price:
                    response = Response({'details': "Your bid must be greater than the last bid for this auction",
                                         'minimum_bid': minimum_price}, status=403)
                else:
                    last_bid_before_this_one = auction[0].last_bid()
                    bid = Bid(price=price, auction=auction[0], time=timezone.now(), bidder=request.user)
                    bid.save()
                    send_mail_to_seller(bid)
                    send_mail_to_last_bid_before_new_one(last_bid_before_this_one, bid)
                    send_mail_to_bidder(bid)

                    response = Response(BidSerializer(bid, many=False).data, status=200)
            else:
                response = Response({'details': 'You should use the key word price to precise the price'}, status=400)

    return response