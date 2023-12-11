import json
import random
import string

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
import subprocess

from django.urls import reverse


def index(request):
    if request.method == "POST":
        data = {
            'session_id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            'old_episode': request.POST.get('episode_old'),
            'new_episode': request.POST.get('episode_new'),
            'characters': []
        }

        n = 1
        while 'user|' + str(n) + '|nameOld' in request.POST:
            data['characters'].append({
                "old": {
                    "name": request.POST['user|' + str(n) + '|nameOld'],
                    "password": request.POST['user|' + str(n) + '|passOld']
                },
                "new": {
                    "name": request.POST['user|' + str(n) + '|nameNew'],
                    "password": request.POST['user|' + str(n) + '|passNew']
                }
            })
            n += 1
        request.session['session_id'] = data['session_id']
        request.session['json'] = json.dumps(data)

        return HttpResponseRedirect(reverse('episodemover:process'))

    else:
        return render(request, "episodemover/index.html")

def process(request):
    p = subprocess.Popen(["venv/bin/python",
                          "episodemover/process.py",
                          "-j", request.session['json'],
                          "symbol"],
                         stdout=open('mover_subprocess.log', 'a'),
                         stderr=open('mover_subprocess.errlog', 'a'))

    return render(request, "episodemover/process.html",
                  {
                      "session_id": request.session['session_id'],
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/episodemover/process", "name": "Перенос эпизода"}
                      ]
                  })