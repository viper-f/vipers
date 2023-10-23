from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.urls import reverse

from advertiser.models import HomeForum
from .forms import LoginForm


def index(request):
    return render(request, "vipers/index.html", {
    })

def user_index(request):
    forums = HomeForum.objects.filter(users=request.user)
    return render(request, "vipers/user_index.html", {
        "username": request.user.username,
        "forums": forums
    })

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('user_index'))
            else:
                return HttpResponseRedirect(reverse('index'))
    else:
        form = LoginForm()
        return render(request, "vipers/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))