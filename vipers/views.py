from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth import logout
from django.urls import reverse

from advertiser.models import HomeForum, BotSession
from .forms import LoginForm, UserSettingsForm


def index(request):
    return render(request, "vipers/index.html", {
    })

@login_required
def user_index(request):
    active_session = BotSession.objects.filter(status='active').first()
    session_id = False
    lock = False

    if active_session is not None:
        lock = True
        home_forum = active_session.home_forum
        if request.user in home_forum.users.all():
            session_id = active_session.session_id

    forums = HomeForum.objects.filter(users=request.user)
    return render(request, "vipers/user_index.html", {
        "username": request.user.username,
        "forums": forums,
        "lock": lock,
        "session": {
            "id": session_id,
            "forum_id": active_session.home_forum.id
        }
    })

@login_required
def user_settings(request):
    if request.method == "POST":
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            old_password = request.POST["old_password"]
            password = request.POST["password"]
            password_repeat = request.POST["password_repeat"]
            if request.user.check_password(old_password):
                if password == password_repeat:
                    request.user.set_password(password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "Your password has been changed")
                else:
                    messages.success(request, "Passwords do not match")
            else:
                messages.error(request, "Wrong current password")
        return HttpResponseRedirect(reverse('user_settings'))
    else:
        form = UserSettingsForm()
        return render(request, "vipers/user_settings.html", {"form": form, "username": request.user.username})

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