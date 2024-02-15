import csv
import json
import random
import string
from datetime import datetime, timedelta

from django.contrib import messages
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.utils.timezone import make_aware

from .forms import AdForm, PartnerForm, ForumForm, AdTemplateForm, ScheduleItemForm, HomeForumForm
from django.urls import reverse
import subprocess

from .models import HomeForum, CustomCredentials, PartnerTopic, AdTemplate, BotSession, ScheduleItem, Forum, \
    ActivityRecord
from .restrictions import check_allowed
from django.conf import settings


@login_required
def advertiser_form(request, id):
    check_allowed(request, id)
    if request.method == "POST":
        form = AdForm(request.POST, forum_id=id)
        if form.is_valid():
            request.session['session_id'] = form.cleaned_data['session_id']
            request.session['url'] = form.cleaned_data['url']

            request.session['custom_credentials'] = form.cleaned_data['custom_credentials']
            request.session['custom_username'] = form.cleaned_data['custom_username']
            request.session['custom_password'] = form.cleaned_data['custom_password']
            request.session['forum_id'] = id

            chosen_template = int(form.cleaned_data['templates'])
            all_templates = list(AdTemplate.objects.filter(home_forum=id).order_by("priority").values_list('id', flat=True))
            if chosen_template != 0:
                all_templates.remove(chosen_template)
                all_templates.insert(0, chosen_template)

            request.session['templates'] = all_templates
            return HttpResponseRedirect(reverse('advertiser:advertiser_process'))
        else:
            print('Something is wrong')
            print(form.errors)
    else:
        active_sessions = BotSession.objects.filter(status='active')
        if not settings.MAX_CONCURRENT:
            max_concurrent = 1
        else:
            max_concurrent = settings.MAX_CONCURRENT
        if len(active_sessions) >= max_concurrent:
            return render(request, "advertiser/stop.html")

        forum = HomeForum.objects.get(pk=id)
        try:
            credentials = CustomCredentials.objects.get(home_forum=id, user=request.user.id, type="home")
        except CustomCredentials.DoesNotExist:
            credentials = False

        form = AdForm(initial={
            'session_id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            'url': forum.ad_topic_url,
            'custom_credentials': credentials != False,
            'custom_username': credentials.username if credentials != False else '',
            'custom_password': credentials.password if credentials != False else '',
            'templates': 0
        }, forum_id=id)
        return render(request, "advertiser/advertiser_form.html",
                      {
                          "form": form,
                          "id": id,
                          "breadcrumbs": [
                              {"link": "/", "name": "Главная"},
                              {"link": "/user-index", "name": "Мои форумы"},
                              {"link": "/advertiser/advertiser/"+str(id), "name": "Запустить рекламу"}
                          ]
                      })

@login_required
def advertiser_process(request):
    forum_id = request.session['forum_id']
    check_allowed(request, forum_id)
    active_sessions = BotSession.objects.filter(status='active')
    print(settings.MAX_CONCURRENT)
    if not settings.MAX_CONCURRENT:
        max_concurrent = 1
    else:
        max_concurrent = settings.MAX_CONCURRENT
    if len(active_sessions) >= max_concurrent:
        return render(request, "advertiser/stop.html")

    session_id = request.session['session_id']
    url = request.session['url']
    templates = request.session['templates']
    templates = [str(i) for i in templates]
    user_id = request.user.id
    if request.session['custom_credentials']:
        custom_credentials = 'true'
    else:
        custom_credentials = 'false'
    custom_username = request.session['custom_username']
    custom_password = request.session['custom_password']

    subprocess.Popen(["venv/bin/python", "advertiser/advertiser_process.py",
                      "-l", url,
                      "-i", session_id,
                      "-t", ','.join(templates),
                      "-c", custom_credentials,
                      "-u", custom_username,
                      "-p", custom_password,
                      '-f', str(forum_id),
                      '-q', str(user_id),
                      "symbol"], stdout=open('subprocess.log', 'a'), stderr=open('subprocess.errlog', 'a'))

    return render(request, "advertiser/advertiser_process.html",
                  {
                      "session_id": session_id,
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/user-index", "name": "Мои форумы"},
                          {"link": "/advertiser/advertiser-process", "name": "Рекламный процесс"}
                      ]
                  })

@login_required
def advertiser_process_observe(request, session_id):
    active_session = BotSession.objects.filter(status='active', session_id=session_id).first()
    check_allowed(request, active_session.home_forum)

    if active_session is None:
        return HttpResponseRedirect(reverse('user_index'))

    return render(request, "advertiser/advertiser_process.html",
                  {
                      "session_id": session_id,
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/user-index", "name": "Мои форумы"},
                          {"link": "/advertiser/observe-advertiser-process/" + session_id, "name": "Рекламный процесс"}
                      ]
                  })

@login_required
def partner_form(request, id):
    check_allowed(request, id)
    if request.method == "POST":
        form = PartnerForm(request.POST)
        if form.is_valid():
            request.session['partner_session_id'] = form.cleaned_data['session_id']
            request.session['partner_urls'] = form.cleaned_data['urls']
            request.session['partner_template'] = form.cleaned_data['template']
            request.session['forum_id'] = id
            return HttpResponseRedirect(reverse('advertiser:partner_process'))
        else:
            print('Something is wrong')
    else:
        partners = PartnerTopic.objects.filter(home_forum=id, type='partner')
        partner_urls = []
        for partner in partners:
            partner_urls.append(partner.url)
        partner_urls = "\n".join(partner_urls)

        form = PartnerForm(initial={
            'session_id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            'urls': partner_urls
        })
        return render(request, "advertiser/partner_form.html",
                      {
                          "form": form,
                          "id": id,
                          "breadcrumbs": [
                              {"link": "/", "name": "Главная"},
                              {"link": "/user-index", "name": "Мои форумы"},
                              {"link": "/advertiser/partner/" + str(id), "name": "Запустить партнерство"}
                          ]
                      })

@login_required
def partner_process(request):
    forum_id = request.session['forum_id']
    check_allowed(request, forum_id)
    session_id = request.session['partner_session_id']
    urls = request.session['partner_urls']
    template = request.session['partner_template']
    user_id = request.user.id
    subprocess.Popen(["venv/bin/python", "advertiser/partner_mailer_process.py",
                      "-u", urls,
                      "-i", session_id,
                      "-t", template,
                      '-f', str(forum_id),
                      '-q', str(user_id),
                      "symbol"], stdout=open('subprocess.log', 'a'), stderr=open('subprocess.errlog', 'a'))

    return render(request, "advertiser/partner_process.html",
                  {
                      "session_id": session_id,
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/user-index", "name": "Мои форумы"},
                          {"link": "/advertiser/partner-process", "name": "Процесс партнерства"}
                      ]
                  })


@login_required
def forum_edit(request, id):
    check_allowed(request, id)
    if request.method == "POST":
        form = ForumForm(request.POST)
        if form.is_valid():

            id = form.cleaned_data['id']
            forum = HomeForum.objects.get(pk=id)

            if forum.domain not in form.cleaned_data['ad_topic_url']:
                messages.error(request, "Домен в ссылке рекламной темы не совпадает с доменом форума")
                return HttpResponseRedirect(reverse('advertiser:forum_edit', kwargs={'id': id}))

            forum.name = form.cleaned_data['name']
            forum.ad_topic_url = form.cleaned_data['ad_topic_url']
            forum.is_rusff = form.cleaned_data['is_rusff']
            forum.ad_topic_template = form.cleaned_data['ad_topic_template']
            forum.create_ad_topic = form.cleaned_data['create_ad_topic']
            forum.save()

            if form.cleaned_data['custom_credentials']:
                try:
                    credentials = CustomCredentials.objects.get(home_forum=forum, user=request.user, type="home")
                    credentials.username = form.cleaned_data['custom_username']
                    credentials.password = form.cleaned_data['custom_password']
                    credentials.save()
                except CustomCredentials.DoesNotExist:
                    credentials = CustomCredentials(
                        home_forum=forum,
                        user=request.user,
                        username=form.cleaned_data['custom_username'],
                        password=form.cleaned_data['custom_password']
                    )
                    credentials.save()
            else:
                try:
                    credentials = CustomCredentials.objects.get(home_forum=forum, user=request.user, type="home")
                    credentials.delete()
                except CustomCredentials.DoesNotExist:
                    pass

            partner_urls = form.cleaned_data['partner_urls']
            new_partner_urls = partner_urls.split("\n")
            existing_partners = PartnerTopic.objects.filter(home_forum=id, type='partner')
            keep = []

            for partner_url in new_partner_urls:
                if partner_url == '':
                    continue
                found = False
                for existing_partner in existing_partners:
                    if existing_partner.url == partner_url:
                        keep.append(existing_partner.id)
                        found = True
                        continue
                if not found:
                    new_partner_url = PartnerTopic(home_forum=forum, url=partner_url)
                    new_partner_url.save()
                    keep.append(new_partner_url.id)

            PartnerTopic.objects.filter(home_forum=id).exclude(pk__in=keep).delete()

            return HttpResponseRedirect(reverse('advertiser:forum_edit', kwargs={'id': id}))
        else:
            print('Something is wrong')
    else:
        forum = HomeForum.objects.get(pk=id)
        try:
            credentials = CustomCredentials.objects.get(home_forum=id, user=request.user.id, type="home")
        except CustomCredentials.DoesNotExist:
            credentials = False

        partners = PartnerTopic.objects.filter(home_forum=id, type='partner')
        partner_urls = []
        for partner in partners:
            partner_urls.append(partner.url)
        partner_urls = "\n".join(partner_urls)

        form = ForumForm(initial={
            'id': forum.id,
            'name': forum.name,
            'domain': forum.domain,
            'ad_topic_url': forum.ad_topic_url,
            'partner_urls': partner_urls,
            'is_rusff': forum.is_rusff,
            'custom_credentials': credentials != False,
            'custom_username': credentials.username if credentials != False else '',
            'custom_password': credentials.password if credentials != False else '',
            'ad_topic_template': forum.ad_topic_template,
            'create_ad_topic': forum.create_ad_topic
        })
        return render(request, "advertiser/forum_form.html",
                      {
                          "form": form,
                          "forum": forum,
                          "breadcrumbs": [
                              {"link": "/", "name": "Главная"},
                              {"link": "/user-index", "name": "Мои форумы"},
                              {"link": "/advertiser/forum-edit/" + str(id), "name": "Редактировать форум"}
                          ]
                      })


@login_required
def ad_templates(request, id):
    check_allowed(request, id)
    if request.method == "POST":
        form = AdTemplateForm(request.POST)
        if form.is_valid():
            forum = HomeForum.objects.get(pk=id)
            template = AdTemplate(home_forum=forum, name=form.cleaned_data['name'],  code=form.cleaned_data['code'])
            template.save()
            return HttpResponseRedirect(reverse('advertiser:ad_templates', kwargs={'id': id}))
        else:
            print('Something is wrong')
    else:
        templates = AdTemplate.objects.filter(home_forum=id).order_by("priority")
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(priority) FROM advertiser_adtemplate WHERE home_forum_id = %s", [id])
            priority = cursor.fetchone()[0]
        if not priority:
            priority = 0
        priority += 1

        for template in templates:
            template.template_view = 'Coming later'

        form = AdTemplateForm(initial={
            'forum_id': id,
            'priority': priority
        })
        return render(request, "advertiser/ad_templates.html",
                      {
                          "form": form,
                          "templates": templates,
                          "id": id,
                          "breadcrumbs": [
                              {"link": "/", "name": "Главная"},
                              {"link": "/user-index", "name": "Мои форумы"},
                              {"link": "/advertiser/templates/" + str(id), "name": "Рекламные шаблоны"}
                          ]
                      })

@login_required
def delete_template(request, id):
    template = AdTemplate.objects.get(pk=id)
    check_allowed(request, template.home_forum)
    template.delete()
    return HttpResponseRedirect(reverse('advertiser:ad_templates', kwargs={'id': template.home_forum.id}))

@login_required
def change_priority_template(request, id):
    check_allowed(request, id)
    priorities = json.loads(request.POST.get('priorities'))

    values = []
    for priority in priorities:
        values.append('('+str(priority[1])+','+str(priority[0])+')')
    values = ','.join(values)
    with connection.cursor() as cursor:
        cursor.execute("update advertiser_adtemplate as templ set priority = c.column_a from (values "+values+") as c(column_a, column_b) where c.column_b = templ.id;")

    return JsonResponse({"result": "success"})

@login_required
def history(request, id, page=0):
    forum = HomeForum.objects.get(pk=id)
    check_allowed(request, forum)
    page_size = 50
    sessions = BotSession.objects.filter(home_forum=forum).order_by('-time_start')[page*page_size:(page+1)*page_size]
    return render(request, "advertiser/history.html",
                  {
                      'sessions': sessions,
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/user-index", "name": "Мои форумы"},
                          {"link": "/advertiser/history/" + str(id), "name": "История"}
                      ]
                  })

@login_required
def stop_session(request, session_id):
    session = BotSession.objects.filter(session_id=session_id).first()
    check_allowed(request, session.home_forum)
    session.stop_signal = True
    session.save()
    return JsonResponse({"result": "success"})


@login_required
def schedule(request, id):
    check_allowed(request, id)

    if request.method == "POST":
        form = ScheduleItemForm(request.POST, forum_id=id, user_id=request.user.id)
        if form.is_valid():
            forum = HomeForum.objects.get(pk=id)
            week_days = form.cleaned_data['week_day']
            week_days = [str(i) for i in week_days]
            week_days = ''.join(week_days)
            time_start = form.cleaned_data['time_start']
            custom_credentials_id = form.cleaned_data['custom_credentials']
            if custom_credentials_id != '':
                custom_credentials = CustomCredentials.objects.get(pk=custom_credentials_id)
            else:
                custom_credentials = None

            schedule_item = ScheduleItem(
                home_forum=forum,
                week_day=week_days,
                time_start=time_start,
                custom_credentials=custom_credentials,
                active=True,
                last_run=make_aware(datetime.fromtimestamp(0))
            )
            schedule_item.save()

            return HttpResponseRedirect(reverse('advertiser:schedule', kwargs={'id': id}))
    else:
        items = ScheduleItem.objects.filter(home_forum=id)
        form = ScheduleItemForm( forum_id=id, user_id=request.user.id, initial={
                'forum_id': id,
        })

        return render(request, "advertiser/schedule.html",
                      {
                          'id': id,
                          'items': items,
                          'form': form,
                          "breadcrumbs": [
                              {"link": "/", "name": "Главная"},
                              {"link": "/user-index", "name": "Мои форумы"},
                              {"link": "/advertiser/schedule/" + str(id), "name": "Расписание"}
                          ]
                      })

@login_required
def forum_add(request):
    if request.method == "POST":
        form = HomeForumForm(request.POST)
        if form.is_valid():

            forum = Forum.objects.get(pk=form.cleaned_data['forum'])
            if forum.domain not in form.cleaned_data['ad_topic_url']:
                messages.error(request, "Домен в ссылке рекламной темы не совпадает с доменом форума")
                return HttpResponseRedirect(reverse('advertiser:forum_add'))


            home_forum = HomeForum(
               name=form.cleaned_data['name'],
               domain=forum.domain,
               ad_topic_url=form.cleaned_data['ad_topic_url'],
               forum=forum,
               is_rusff=form.cleaned_data['is_rusff'],
            )
            home_forum.save()
            home_forum.users.set(form.cleaned_data['users'])
            home_forum.save()
            return HttpResponseRedirect(reverse('advertiser:forum_edit', kwargs={'id': home_forum.id}))
        else:
            for error in form.errors:
                messages.error(request, error)
                return HttpResponseRedirect(reverse('advertiser:forum_add'))
            print(form.errors)
    else:
        form = HomeForumForm()
        return render(request, "advertiser/forum_add.html",
                      {
                          "form": form,
                          "breadcrumbs": [
                              {"link": "/", "name": "Главная"},
                              {"link": "/user-index", "name": "Мои форумы"},
                              {"link": "/advertiser/forum-add/", "name": "Добавить форум"}
                          ]
                      })

def activity_list(request):
    max_record = ActivityRecord.objects.latest('day')
    max_day = max_record.day
    records = ActivityRecord.objects.filter(day=max_day).order_by('-activity')
    return render(request, "advertiser/activity.html",
                  {
                      "records": records,
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/advertiser/activity", "name": "Активность форумов"}
                      ]
                  })

def forum_activity(request, id):
    forum = Forum.objects.get(pk=id)
    records = ActivityRecord.objects.filter(forum=id).order_by('-day').values("activity", "day")
    data = {
        "labels": [],
        "datasets": [{
            "data": [],
            "label": "activity"
        }]
    }
    for record in reversed(records):
        data['labels'].append(record['day'].strftime('%Y-%m-%d'))
        data['datasets'][0]['data'].append(record['activity'])
    return render(request, "advertiser/forum_activity.html",
                  {
                      "records": records,
                      "forum": forum,
                      "data": data,
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/advertiser/activity", "name": "Активность форумов"},
                          {"link": "/advertiser/activity/"+str(id), "name": "Активность форума "}
                      ]
                  })



def download_activity(request):
    forum_id = ActivityRecord.objects.last().forum.id
    dates = ActivityRecord.objects.filter(forum_id=forum_id).values_list('day', flat=True)
    fields = []
    for date in dates:
        fields.append("max(t.activity) filter (where day = '"+date.strftime('%Y-%m-%d')+"') as "+'"'+date.strftime('%Y-%m-%d')+'"')
    fields = ', '.join(fields)
    query = "select domain, board_id, to_char(to_timestamp(board_found), 'yyyy-mm-dd hh24:ii:ss'), "+fields+" from (select * from advertiser_activityrecord) t join advertiser_forum on advertiser_forum.id = t.forum_id group by forum_id, domain, board_id, board_found order by forum_id"

    #return HttpResponse(query)

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="forum_activity.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['Forum URL', 'Board ID', 'Forum Created']+list(dates))

    with connection.cursor() as cursor:
        cursor.execute(query)
        row = 0
        while row is not None:
            row = cursor.fetchone()
            if row is None:
                break
            writer.writerow(row)

    return response

