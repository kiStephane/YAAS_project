# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


def register(request):
    if request.method == "POST":
        if request.POST.has_key("username") and request.POST.has_key("password"):
            user = User.objects.create_user(username=request.POST["username"],
                                            email=request.POST["email"],
                                            password=request.POST["password"])
            return render_to_response("userprofile.html", {"user": user},
                                      context_instance=RequestContext(request)
            )

    elif request.method == "GET":
        return render_to_response("register.html", {},
                                  context_instance=RequestContext(request)
        )


def sign_in(request):
    if request.method == "POST":
        if request.POST.has_key("username") and request.POST.has_key("password"):
            user = authenticate(username=request.POST["username"], password=request.POST["password"])
            if user is not None:
                # the password verified for the user
                if user.is_active:
                    print("User is valid, active and authenticated")
                    request.session['user_username'] = user.username
                    request.session['user_password'] = user.password
                    return render_to_response("userprofile.html", {"user": user},
                                              context_instance=RequestContext(request)
                    )
                else:
                    info = "The password is valid, but the account has been disabled!"
                    return render_to_response("signin.html", {"info": info},
                                              context_instance=RequestContext(request)
                    )
        else:
            # the authentication system was unable to verify the username and password
            info = "The username and password were incorrect."
            return render_to_response("signin.html", {"info": info},
                                      context_instance=RequestContext(request)
            )

    elif request.method == "GET":
        return render_to_response("signin.html", {},
                                  context_instance=RequestContext(request)
        )

    return render_to_response("index.html", {},
                              context_instance=RequestContext(request)
    )


def edit_profile(request):
    if request.method == "GET":
        return render_to_response("editprofile.html", {"username": request.session['user_username']},
                                  context_instance=RequestContext(request)
        )
    elif request.method == "POST":
        if request.POST.has_key("email") and request.POST.has_key("password"):
            new_email = request.POST["email"]
            new_password = request.POST["password"]
            print request.session['user_username']
            print request.session['user_password']
            user = authenticate(username=request.session['user_username'], password=request.session['user_password'])
            if user is not None:
                print "Hereeeeeeeee"
                user.password = new_password
                user.email = new_email
                user.save()
                request.session['user'] = user
                return render_to_response("userprofile.html", {"user": user},
                                              context_instance=RequestContext(request)
                )

        return render_to_response("editprofile.html", {"username": request.session['user_username']},
                                  context_instance=RequestContext(request)
        )


def show_home(request):
    return render_to_response("index.html", {},
                              context_instance=RequestContext(request)
    )