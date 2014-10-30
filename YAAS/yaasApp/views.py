# Create your views here.
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import logout
from django.utils import translation
from django.utils.translation import ugettext as _
from django.core.mail import send_mail

from yaasApp.forms import *
from yaasApp.search import get_query


FROM_EMAIL = "noreply@yaas.com"


@login_required
def create_auction(request):
    if not request.method == 'POST':
        return render_to_response('createauction.html', {'form': AuctionCreationForm(),
                                                         'username': request.user.username},
                                  context_instance=RequestContext(request))
    else:
        form = AuctionCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            auction_title = cd['title']
            auction_desc = cd['description']
            auction_min_price = cd['minimum_price']
            auction_deadline = cd['deadline']
            request.session['auction_data'] = cd
            return render_to_response('confirmation.html', {'form': ConfirmationForm(),
                                                            'auction_title': auction_title,
                                                            'auction_desc': auction_desc,
                                                            'auction_min_price': auction_min_price,
                                                            'auction_deadline': auction_deadline,
                                                            'username': request.user.username},
                                      context_instance=RequestContext(request))
        else:
            return render_to_response('createauction.html', {'form': form,
                                                             'username': request.user.username},
                                      context_instance=RequestContext(request))


@login_required
def save_auction(request):
    option = request.POST.get('option', '')
    if option == 'Yes':
        data = request.session['auction_data']
        auction = Auction(title=data['title'],
                          description=data["description"],
                          creation_date=data["creation_date"],
                          deadline=data["deadline"],
                          minimum_price=data["minimum_price"],
                          seller=request.user)
        auction.save()
        send_mail("New auction <" + data['title'] + "> created",
                  "Your new auction <" + data['title'] + "> has been created",
                  FROM_EMAIL, [request.user.email], fail_silently=False)
        return render_to_response('done.html', {'message': "New auction has been saved",
                                                'username': request.user.username},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('createauction.html', {'form': AuctionCreationForm(),
                                                         'error': "Auction has not been saved",
                                                         'username': request.user.username},
                                  context_instance=RequestContext(request))


@login_required
def edit_auction(request, a_id):
    auctions = Auction.objects.filter(id=a_id).filter(state=1)
    if not auctions.count() is 0:
        auction = auctions[0]
        if auction.seller == request.user:
            print request.method
            if request.method == "GET":
                return render_to_response('editauction.html', {'auction': auction,
                                                               'username': request.user.username},
                                          context_instance=RequestContext(request))
            elif request.method == "POST":
                auction.description = request.POST.get("description")
                auction.version += 1
                auction.save()
            else:
                return HttpResponseBadRequest()
        else:
            request.session["message_to_profile"] = _("You cannot edit this auction because you are not the seller")
    else:
        request.session["message_to_profile"] = _("This auction does not exists")

    return HttpResponseRedirect("/profile/")


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            request.session["message_to_home"] = _("New User is created. Please Login")
            return HttpResponseRedirect("/home/")
    else:
        form = UserCreationForm()
    return render_to_response("registration.html", {'form': form}, context_instance=RequestContext(request))


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            request.session["message_to_profile"] = "Password set ! ! !"
            return HttpResponseRedirect("/profile/")
    else:
        form = PasswordChangeForm(user=request.user)
    return render_to_response("changepassword.html", {'form': form,
                                                      'username': request.user.username},
                              context_instance=RequestContext(request))


@login_required
def edit_profile(request):
    """
    This views allow the user to change he/she email address.
    """
    if request.POST:
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/profile/')
    else:
        form = EditProfileForm()
    return render_to_response('editprofile.html', {'form': form,
                                                   'username': request.user.username},
                              context_instance=RequestContext(request))


def sign_in(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        next_to = request.GET.get('next', '/home/')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect(next_to)
        else:
            error = _("Wrong username or password ! ! !")
            return render_to_response("signin.html", {'error': error}, context_instance=RequestContext(request))

    else:
        error = _("Please Sign in")
        return render_to_response("signin.html", {'error': error}, context_instance=RequestContext(request))


@login_required
def sign_out(request):
    logout(request, next_page="/home/")
    return HttpResponseRedirect("/home/")


def show_profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/signin/?next=%s' % request.path)
    else:
        user = request.user
        auctions = user.auction_set.all()
        bids = user.bid_set.all()
        message = request.session.get("message_to_profile")
        request.session["message_to_profile"] = None
        return render_to_response("userprofile.html", {"username": user.username,
                                                       "user_email": user.email,
                                                       "auctions": auctions,
                                                       "bids": bids,
                                                       "msg": message},
                                  context_instance=RequestContext(request)
        )


def show_home(request):
    translation.activate(request.session.get("lang", 'en'))
    auctions = Auction.objects.all().filter(state=1)
    error = request.session.get("error_to_home")
    message = request.session.get("message_to_home")
    request.session["error_to_home"] = None
    request.session["message_to_home"] = None
    return render_to_response("index.html", {"auctions": auctions,
                                             "username": request.user.username,
                                             "error": error,
                                             "msg": message},
                              context_instance=RequestContext(request)
    )


def browse_result_pagination(request):
    translation.activate(request.session.get("lang", 'en'))
    result = Auction.objects.all().filter(state=1)
    paginator = Paginator(result, 10)  # Show 10 per page

    page = request.GET.get('page')
    try:
        auctions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        auctions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        auctions = paginator.page(paginator.num_pages)

    return render_to_response('browse_results.html', {"auctions": auctions}, context_instance=RequestContext(request))


def show_auction(request, a_id):
    auction = Auction.objects.filter(id=a_id)
    if auction.count() == 1:
        if auction[0].state == 1:
            error = request.session.get("error_to_auction_show")
            request.session["error_to_auction_show"] = None
            last = auction[0].last_bid_price()
            return render_to_response("auction.html", {"auction": auction[0],
                                                       'error': error,
                                                       "last_bid": last,
                                                       "username": request.user.username},
                                      context_instance=RequestContext(request))
        else:
            request.session["error_to_home"] = "Cannot access this auction: BANNED"
    else:
        request.session["error_to_home"] = "Auction (id=" + str(a_id) + ") does not exist !"
    return HttpResponseRedirect("/home/")


@login_required
def create_bid(request, a_id):
    auction = Auction.objects.filter(id=a_id).filter(state=1)
    if not request.method == 'POST':
        if len(auction) == 0:
            request.session["error_to_home"] = _("The auction you want to bid for does not exist !")
            return HttpResponseRedirect('/home/')
        elif auction[0].seller == request.user:
            request.session["error_to_auction_show"] = _("You cannot bid because you are the seller !")
            return HttpResponseRedirect('/auction/' + str(a_id))
        else:
            form = BidCreationForm({"auction_id": a_id})
            request.session["auction_version"] = auction[0].version
            request.session["number_of_bids"] = len(auction[0].bid_set.all())
            error = request.session.get('error_to_create_bid')
            request.session["error_to_create_bid"] = None

            return render_to_response('createbid.html', {'form': form,
                                                         'error': error,
                                                         'username': request.user.username,
                                                         'minimum_bid': auction[0].minimum_bid_price(),
                                                         'auction_id': a_id},
                                      context_instance=RequestContext(request))
    else:
        form = BidCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            request.session['bid_data'] = cd

            if auction[0].last_bidder_username() == request.user.username:
                request.session["message_to_profile"] = "You cannot bid for an already winning auction!"
                return HttpResponseRedirect("/profile/")
            elif auction[0].is_due():  # TODO remove comment
                request.session["error_to_auction_show"] = "This auction is due"
                return HttpResponseRedirect("/auction/" + str(auction[0].id) + "/")

            elif request.session.get("auction_version") == auction[0].version and request.session.get(
                    "number_of_bids") == len(auction[0].bid_set.all()):
                last_bid_before_this_one = auction[0].last_bid()
                bid = Bid(price=int(cd["price"]), auction=auction[0], bidder=request.user, time=timezone.now())
                bid.save()
                message = "New bid has been saved"

                send_mail_to_seller(bid)
                send_mail_to_last_bid_before_new_one(last_bid_before_this_one, bid)
                send_mail_to_bidder(bid)

                return render_to_response('done.html', {'message': message,
                                                        'username': request.user.username},
                                          context_instance=RequestContext(request))

            elif request.session.get("auction_version") != auction[0].version:

                form = ConfirmationForm()
                message = _("The auction description has changed")
                return render_to_response('confbid.html', {'form': form,
                                                           'message': message,
                                                           'auction_id': auction[0].id,
                                                           'auction_desc': auction[0].description,
                                                           'auction_title': auction[0].title,
                                                           'username': request.user.username},
                                          context_instance=RequestContext(request))
        else:
            return render_to_response('createbid.html', {'form': BidCreationForm(),
                                                         'error': "Not valid data",
                                                         'last_bid_price': auction[0].last_bid_price(),
                                                         'username': request.user.username},
                                      context_instance=RequestContext(request))


@login_required
def save_bid(request):
    option = request.POST.get('option', '')
    data = request.session.get('bid_data')
    if option == 'Yes':

        auction = Auction.objects.get(id=data["auction_id"])

        if request.session.get("number_of_bids") == len(auction.bid_set.all()):
            last_bid_before_this_one = auction.last_bid()
            bid = Bid(auction=auction, bidder=request.user, time=timezone.now(),
                      price=data["price"])
            bid.save()
            message = _("New bid registered !!!")

            send_mail_to_seller(bid)
            send_mail_to_last_bid_before_new_one(last_bid_before_this_one, bid)
            send_mail_to_bidder(bid)

            return render_to_response('done.html', {'message': message,
                                                    'username': request.user.username},
                                      context_instance=RequestContext(request))
        else:
            request.session['error_to_create_bid'] = _("Someone bid before you. Bid again !")
            return HttpResponseRedirect("/createbid/" + str(data["auction_id"]))
    else:
        request.session["error_to_create_bid"] = "Bid has not been saved"
        return HttpResponseRedirect("/createbid/" + str(data["auction_id"]))


def send_mail_to_seller(bid, sub=None, body=None):
    if not body:
        email_body = "Hello, " + bid.auction.seller.username + ".\n Someone bid for your auction"
    else:
        email_body = body
    to_email = bid.auction.seller.email
    if not sub:
        subject = "New bid for your auction <" + bid.auction.title + ">"
    else:
        subject = sub
    send_mail(subject, email_body, FROM_EMAIL, [to_email], fail_silently=False)


def send_mail_to_bidder(bid, sub=None, body=None):
    if not body:
        email_body = "Hello, " + bid.bidder.username + ".\n Bid created !!!"
    else:
        email_body = body

    to_email = bid.auction.last_bid().bidder.email
    if not sub:
        subject = "New bid saved. Auction <" + bid.auction.title + ">"
    else:
        subject = sub
    send_mail(subject, email_body, FROM_EMAIL, [to_email], fail_silently=False)


def send_mail_to_last_bid_before_new_one(last_bid_before_new_one, bid):
    if last_bid_before_new_one:
        email_body = "Hello, " + last_bid_before_new_one.bidder.username + ".\n Bid exceeded !!!"
        to_email = last_bid_before_new_one.bidder.email
        subject = "Your bid has been exceeded. Auction <" + bid.auction.title + ">"
        send_mail(subject, email_body, FROM_EMAIL, [to_email], fail_silently=False)


def search(request):
    if 'q' in request.GET:
        query_string = request.GET["q"]
        entry_query = get_query(query_string, ['title'])
        found_entries = None
        if entry_query:
            found_entries = Auction.objects.filter(entry_query)
            request.session["search_result"] = found_entries
        error = None

        if not found_entries is None:
            if found_entries.count() == 0:
                error = _('Nothing found in the database')
        else:
            error = _('Nothing found in the database')
        request.session["search_error"] = error
        return HttpResponseRedirect("/results/?page=1")
    else:
        return HttpResponseBadRequest("Bad Request")


def search_result_pagination(request):
    result = request.session.get("search_result")
    paginator = Paginator(result, 10)  # Show 10 per page

    page = request.GET.get('page')
    try:
        auctions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        auctions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        auctions = paginator.page(paginator.num_pages)

    return render_to_response('search_results.html', {"auctions": auctions}, context_instance=RequestContext(request))


def select_lang(request, lang):
    request.session['lang'] = lang
    return HttpResponseRedirect("/home/")


@permission_required('yaasApp.can_ban', login_url="/signin/")
def ban_auction(request, a_id):
    auction = get_object_or_404(Auction, id=a_id)
    if auction.ban():
        auction.save()
        send_mail_to_seller(auction.last_bid(), sub="Your auction <" + auction.title + "> has been banned")
        for bid in auction.bid_set.all():
            sub = 'Auction <' + bid.auction.title + '> has been banned'
            send_mail_to_bidder(bid, sub=sub, body="")

        return HttpResponseRedirect('/home/')
    else:
        return render_to_response("auction.html", {"auction": auction,
                                                   'error': "You can only ban active auctions",
                                                   "last_bid": auction.last_bid(),
                                                   "username": request.user.username},
                                  context_instance=RequestContext(request))