import os
import string
import subprocess
import random

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse

from intellect.Trainer import Trainer
from intellect.forms import CrawlerForm
from intellect.models import CrawlSession, Page, TrainingSet


def index(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")

    sql = ('select intellect_page.control_session_id, intellect_crawlsession.time_start, intellect_crawlsession.session_id, count(*) as page_number, count(CASE WHEN verified THEN 1 END) as verified_number, intellect_trainingset.id as training_set from intellect_page join intellect_crawlsession on intellect_page.control_session_id = intellect_crawlsession.id left join intellect_trainingset on intellect_trainingset.control_session_id = intellect_crawlsession.id group by intellect_page.control_session_id, intellect_crawlsession.time_start, intellect_crawlsession.session_id, intellect_trainingset.id order by intellect_crawlsession.time_start desc limit 5')
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
        "id": id,
        "session_id": session.session_id,
        "session_date": session.time_start,
        "records": pages
    })

def render_page_redirect(request, id):
   # session = CrawlSession.objects.get(pk=id)
    pages = list(Page.objects.filter(control_session_id=id).values_list('id', flat=True))
    pages = ','.join(str(x) for x in pages)
    pages = '[' + pages + ']'
    return render(request, "intellect/page_redirect.html", {
        "pages": pages
    })



def render_page(request, id):
    page = Page.objects.get(pk=id)
    f = open(page.file_path, "r", encoding="windows-1251")
    content = f.read()
    content = content.replace('<body>', '<body><div id="page-scroller" style="z-index: 101; position: fixed;top: 0;left: 0; width: calc(100% - 2rem); background: #fff;text-align: center;box-shadow: 0 0 5px #ccc;padding: 1rem;font-size: 1.5rem;"><a style="float: left; cursor: pointer" onclick="pageprev()">Назад</a><a style="float: right; cursor: pointer" onclick="pagenext()">Вперед</a> Проверить форум</div>\n<script>'
                                        '\nfunction pageCheck(b, element) {console.log(element.querySelector("a[href]").href.split("=")[1]); fetch("/intellect/correct/'+str(id)+'/"+element.querySelector("a[href]").href.split("=")[1], { method: "GET" }).then(b.innerText = "V")}'
                                        '\nfunction pageprev() {pages = JSON.parse(localStorage.getItem("pages")); index = parseInt(localStorage.getItem("index")); index -= 1; localStorage.setItem("index", index); window.location = "/intellect/page/"+pages[index];}'
                                        '\nfunction pagenext() {pages = JSON.parse(localStorage.getItem("pages")); index = parseInt(localStorage.getItem("index")); index += 1; if (pages.length <= index) {window.location = "/intellect"} else { localStorage.setItem("index", index); window.location = "/intellect/page/"+pages[index];}}'
                                        '\n</script>')
    content = content.replace('<div class="tclcon">', '<div class="tclcon"><a style="cursor: pointer; color: green;padding: 3px;" onclick="pageCheck(this, this.parentElement)">=></a>')
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


def correct_id(request, page_id, topic_id):
    page = Page.objects.get(pk=page_id)
    page.corrected_topic_id = topic_id
    page.verified = True
    page.save()
    return JsonResponse({"corrected": "True"})

def download_training_set(request, id, filename):
    training_set = TrainingSet.objects.get(pk=id)
    file_path = training_set.folder_path.replace('./..', './') + '/' + filename + '.pickle'
    print(file_path)
   # if os.path.exists(file_path):
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/octet-stream")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response
   # else:
   #      raise Http404