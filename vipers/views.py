from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth import logout
from django.urls import reverse

from advertiser.models import HomeForum, BotSession
from .forms import LoginForm, UserSettingsForm


def index(request):
    return render(request, "vipers/index.html")

@login_required
def user_index(request):
    active_sessions = BotSession.objects.filter(status='active')
    lock = False

    try:
        max_concurrent = settings.MAX_CONCURRENT
    except:
        max_concurrent = 1

    sessions = {}
    if len(active_sessions) >= max_concurrent:
        lock = True
        
    for active_session in active_sessions:
        if request.user in active_session.home_forum.users.all():
            if active_session.home_forum.id not in sessions:
                sessions[active_session.home_forum.id] = {}
            sessions[active_session.home_forum.id][active_session.type] = active_session.session_id

    forums = HomeForum.objects.filter(users=request.user).order_by("id")
    forums_visible = []
    forums_hidden = []

    for forum in forums:
        if forum.is_hidden:
            forums_hidden.append(forum)
            continue
        if forum.id in sessions:
            if 'advertiser' in sessions[forum.id]:
                forum.session_advertiser = sessions[forum.id]['advertiser']
                forum.session_advertiser_teminate = True
            else:
                forum.session_advertiser = False
                 forum.session_advertiser_teminate = False

            if 'partner' in sessions[forum.id]:
                forum.session_partner = sessions[forum.id]['partner']
            else:
                forum.session_partner = False
        else:
            forum.session_advertiser = False
             forum.session_advertiser_teminate = False
            forum.session_partner = False
        forums_visible.append(forum)

    return render(request, "vipers/user_index.html", {
        "username": request.user.username,
        "forums": forums_visible,
        "hidden_forums": forums_hidden,
        "lock": lock,
        "breadcrumbs": [{"link": "/", "name": "Главная"}, {"link": "/user-index", "name": "Мои форумы"}]
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
        return render(request, "vipers/user_settings.html",
                      {
                          "form": form,
                       "username": request.user.username,
                          "breadcrumbs": [{"link": "/", "name": "Главная"},
                                          {"link": "/user-settings", "name": "Мои настройки"}]
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


