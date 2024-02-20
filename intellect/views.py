import string
import subprocess
import random

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from intellect.forms import CrawlerForm
from intellect.models import CrawlSession, Page


def index(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")

    sql = ('select control_session_id, intellect_crawlsession.time_start, intellect_crawlsession.session_id, '
           'count(*) as page_number, count(CASE WHEN verified THEN 1 END) as verified_number from intellect_page join '
           'intellect_crawlsession on intellect_page.control_session_id = intellect_crawlsession.id group by '
           'control_session_id, intellect_crawlsession.time_start, intellect_crawlsession.session_id order by '
           'intellect_crawlsession.time_start desc limit 5')
    records = []
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [x.name for x in cursor.description]
        for row in cursor:
            records.append(dict(zip(columns, row)))
    return render(request, "intellect/index.html", {"records": records})


def session(request, id):
    session = CrawlSession.objects.get(pk=id)
    pages = Page.objects.filter(control_session=session)
    return render(request, "intellect/session.html", {
        "session_id": session.session_id,
        "session_date": session.time_start,
        "records": pages
    })


def render_page(request, id):
    page = Page.objects.get(pk=id)
    f = open(page.file_path, "r", encoding="windows-1251")
    content = f.read()
    return HttpResponse(content)


@login_required
def crawler_form(request):
    # check_allowed(request, id)
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


def verify(request, id):
    page = Page.objects.get(pk=id)
    page.verified = True
    page.save()
    return JsonResponse({"verified": "True"})