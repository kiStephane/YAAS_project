# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import logout
from datetime import datetime
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
            request.session['auction_date'] = cd
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
        data = request.session['auction_date']
        auction = Auction(title=data['title'],
                          description=data["description"],
                          creation_date=timezone.now(),
                          deadline=data["deadline"],
                          minimum_price=data["minimum_price"],
                          seller=request.user)
        auction.save()
        message = "New auction has been saved"
        return render_to_response('done.html', {'message': message,
                                                'username': request.user.username},
                                  context_instance=RequestContext(request))
    else:
        error = "Auction is not saved"
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
                auction.save()

    return HttpResponseRedirect("/profile/")


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            message = "New User is created. Please Login"
            return render_to_response("index.html", {'msg': message}, context_instance=RequestContext(request))
    else:
        form = UserCreationForm()
    return render_to_response("registration.html", {'form': form}, context_instance=RequestContext(request))


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            message = "Password set" #TODO Find a way to send this message
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
        if user is not None and user.is_active:
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
        return render_to_response("userprofile.html", {"username": user.username,
                                                       "user_email": user.email,
                                                       "auctions": auctions},
                                  context_instance=RequestContext(request)
        )


def show_home(request):
    auctions = Auction.objects.all()
    msg = request.session.get("error")
    return render_to_response("index.html", {"auctions": auctions,
                                             "username": request.user.username,
                                             "msg": msg},
                              context_instance=RequestContext(request)
    )


def show_auction(request, a_id):
    auction = Auction.objects.filter(id=a_id)
    if auction.count() == 1:
        return render_to_response("auction.html", {"auction": auction[0]}, context_instance=RequestContext(request))
    else:
        request.session["error"] = "This auction don't exist !"
        return HttpResponseRedirect("/home/")
