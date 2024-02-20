import string
import subprocess
import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from intellect.forms import CrawlerForm
from intellect.models import CrawlSession


def index(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    return render(request, "intellect/index.html")
    
@login_required
def crawler_form(request):
    #check_allowed(request, id)
    if request.method == "POST":
        form = CrawlerForm(request.POST)
        if form.is_valid():
            request.session['session_id'] = form.cleaned_data['session_id']
            request.session['dead_included'] = form.cleaned_data['dead_included']
            return HttpResponseRedirect(reverse('intellect:crawler_process'))
        else:
            print('Something is wrong')
            print(form.errors)
    else:
        active_sessions = CrawlSession.objects.filter(status='active')
        if len(active_sessions) > 0:
            return render(request, "advertiser/stop.html")

        form = CrawlerForm(initial={
            'session_id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        })
        return render(request, "intellect/crawler_form.html",
                      {
                          "form": form,
                          "breadcrumbs": [
                              {"link": "/", "name": "Главная"},
                              {"link": "/intellect", "name": "Мозги"},
                              {"link": "/intellect/crawler-start", "name": "Запустить кроулинг"}
                          ]
                      })

@login_required
def crawl_process(request):
   # check_allowed(request, forum_id)
    active_sessions = CrawlSession.objects.filter(status='active')
    if len(active_sessions) > 0:
        return render(request, "advertiser/stop.html")

    session_id = request.session['session_id']
    dead_included = str(int(request.session['dead_included']))

    subprocess.Popen(["venv/bin/python", "intellect/crawler_process.py",
                      "-i", session_id,
                      "-d", dead_included,
                      "symbol"], stdout=open('subprocess.log', 'a'), stderr=open('subprocess.errlog', 'a'))

    return render(request, "advertiser/advertiser_process.html",
                  {
                      "session_id": session_id,
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/intellect", "name": "Мозги"},
                          {"link": "/intellect/crawler-process", "name": "Кроулинг"}
                      ]
                  })


