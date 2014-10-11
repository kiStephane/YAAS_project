# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import logout
from yaasApp.forms import *
from django.utils import timezone


@login_required
def create_auction(request):
    if not request.method == 'POST':
        form = AuctionCreationForm()
        return render_to_response('createauction.html', {'form': form,
                                                         'username': request.user.username},
                                  context_instance=RequestContext(request))
    else:
        form = AuctionCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            auction_title = cd['title']
            request.session['auction_data'] = cd
            form = ConfirmationForm()
            return render_to_response('confirmation.html', {'form': form,
                                                            'auction_title': auction_title,
                                                            'username': request.user.username},
                                      context_instance=RequestContext(request))
        else:
            form = AuctionCreationForm()
            return render_to_response('createauction.html', {'form': form,
                                                             'error': "Not valid data",
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
        message = "New auction has been saved"
        return render_to_response('done.html', {'message': message,
                                                'username': request.user.username},
                                  context_instance=RequestContext(request))
    else:
        error = "Auction has not been saved"
        form = AuctionCreationForm()
        return render_to_response('createauction.html', {'form': form,
                                                         'error': error,
                                                         'username': request.user.username},
                                  context_instance=RequestContext(request))


@login_required
def edit_auction(request, a_id):
    auction = Auction.objects.get(id=a_id)
    if not auction is None:
        if auction in request.user.auction_set.all():
            if request.method != "POST":
                return render_to_response('editauction.html', {'auction': auction,
                                                               'username': request.user.username},
                                          context_instance=RequestContext(request))
            else:
                auction.description = request.POST.get("description")
                auction.version += 1
                auction.save()

    return HttpResponseRedirect("/profile/")


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            request.session["message_to_home"] = "New User is created. Please Login"
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
    if request.POST:
        user_form = EditProfileForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return HttpResponseRedirect('/profile/')
    else:
        user_form = EditProfileForm()
    return render_to_response('editprofile.html', {'form': user_form,
                                                   'username': request.user.username},
                              context_instance=RequestContext(request))


def sign_in(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        next_to = request.GET.get('next', '/home/')
        user = authenticate(username=username, password=password)
        if user is not None and is_active:
            auth.login(request, user)
            return HttpResponseRedirect(next_to)
        else:
            error = "Wrong username or password ! ! !"
            return render_to_response("signin.html", {'error': error}, context_instance=RequestContext(request))

    else:
        error = "Please Sign in"
        return render_to_response("signin.html", {'error': error}, context_instance=RequestContext(request))


def sign_out(request):
    logout(request, template_name="index.html")
    return HttpResponseRedirect("/home/")


def show_profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/signin/?next=%s' % request.path)
    else:
        user = request.user
        auctions = user.auction_set.all()
        message = request.session.get("message_to_profile")
        return render_to_response("userprofile.html", {"username": user.username,
                                                       "user_email": user.email,
                                                       "auctions": auctions,
                                                       "msg": message},
                                  context_instance=RequestContext(request)
        )


def show_home(request):
    auctions = Auction.objects.all()
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


def show_auction(request, a_id):
    # TODO Show the last bid
    auction = Auction.objects.filter(id=a_id)
    if auction.count() == 1:
        error = request.session.get("error_to_auction_show")
        request.session["error_to_auction_show"] = None
        return render_to_response("auction.html", {"auction": auction[0],
                                                   'error': error,
                                                   "username": request.user.username},
                                  context_instance=RequestContext(request))
    else:
        request.session["error_to_home"] = "Auction (id=" + str(a_id) + ") does not exist !"
        return HttpResponseRedirect("/home/")


@login_required
def create_bid(request, a_id):
    auction = Auction.objects.filter(id=a_id)
    if not request.method == 'POST':
        if len(auction) == 0:
            request.session["error_to_home"] = "The auction you want to bid for does not exist !"
            return HttpResponseRedirect('/home/')
        elif auction[0].seller == request.user:
            request.session["error_to_auction_show"] = "You cannot bid because you are the seller !"
            return HttpResponseRedirect('/auction/' + str(a_id))
        else:
            form = BidCreationForm({"auction_id": a_id})
            request.session["auction_version"] = auction[0].version
            return render_to_response('createbid.html', {'form': form,
                                                         'username': request.user.username,
                                                         'auction_id': a_id},
                                      context_instance=RequestContext(request))
    else:
        form = BidCreationForm(request.POST)
        print request.POST
        if form.is_valid():
            cd = form.cleaned_data
            request.session['bid_data'] = cd

            if request.session.get("auction_version") == auction[0].version:
                bid = Bid(price=int(cd["price"]), auction=auction[0], bidder=request.user, time=timezone.now())
                bid.save()
                # TODO Redirect the user to done.html
                message = "New bid has been saved"
                return render_to_response('done.html', {'message': message,
                                                        'username': request.user.username},
                                          context_instance=RequestContext(request))
            else:
                form = ConfirmationForm()
                # TODO Inform the user that the description have changed
                # TODO If someone has bid before the current user then send him back to the auction page
                # with the message: "New bid before you, bid again"

                message = "The auction has changed"
                return render_to_response('confbid.html', {'form': form,
                                                           'auction_id': auction[0].id,
                                                           'auction_desc': auction[0].description,
                                                           'auction_title': auction[0].title,
                                                           'username': request.user.username},
                                          context_instance=RequestContext(request))
        else:
            form = BidCreationForm()
            return render_to_response('createbid.html', {'form': form,
                                                         'error': "Not valid data",
                                                         'username': request.user.username},
                                      context_instance=RequestContext(request))


@login_required
def save_bid(request):
    option = request.POST.get('option', '')
    if option == 'Yes':
        pass
    else:
        pass