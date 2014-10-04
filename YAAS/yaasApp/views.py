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
            message = "Password set"
            return render_to_response("userprofile.html", {'msg': message}, context_instance=RequestContext(request))
        else:
            print 'Non valid'
    else:
        form = PasswordChangeForm(user=request.user)
    return render_to_response("changepassword.html", {'form': form},
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
    return render_to_response('editprofile.html', {'form': user_form}, context_instance=RequestContext(request))


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
        return render_to_response("userprofile.html", {"user_name": user.username, "user_email": user.email},
                                  context_instance=RequestContext(request)
        )


def show_home(request):
    return render_to_response("index.html", {},
                              context_instance=RequestContext(request)
    )