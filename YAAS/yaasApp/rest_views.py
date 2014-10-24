import json

from rest_framework.decorators import authentication_classes, permission_classes, renderer_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


__author__ = 'stephaneki'
from yaasApp.models import Auction
from yaasApp.search import get_query
from yaasApp.serializers import AuctionSerializer

from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import *


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# @csrf_exempt
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
        return Response({'details': 'The auction you want to bid for does not exist !'}, status=400)
    else:
        if auction[0].seller.username == request.user.username:
            # a seller cannot bid for his own auction
            return Response({'details': 'A seller cannot bid for his own auction'}, status=403)
        elif auction[0].last_bidder_username() == request.user.username:
            # a bidder cannot bid an already winning auction
            return Response({'details': "Cannot bid for already winning auction"}, status=403)
        else:
            if 'price' in request.POST:
                price = json.loads(request.POST.get('price'))
                minimum_price = auction[0].minimum_bid_price()
                if minimum_price > price:
                    return Response({'details': "Your bid must be greater than the last bid for this auction",
                                     'minimum_bid': minimum_price}, status=403)
            else:
                pass

