import subprocess

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from intellect.models import CrawlSession


def index(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('vipers:index'))

@login_required
def crawl_process(request):
   # check_allowed(request, forum_id)
    active_sessions = CrawlSession.objects.filter(status='active')
    if len(active_sessions) > 0:
        return render(request, "advertiser/stop.html")

    session_id = request.session['session_id']
    dead_included = int(request.sesson['dead_included'])

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


