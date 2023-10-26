import random
import string

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import AdForm, PartnerForm, ForumForm, AdTemplateForm
from django.urls import reverse
import subprocess

from .models import HomeForum, CustomCredentials, PartnerTopic, AdTemplate, BotSession
from .restrictions import check_allowed


@login_required
def advertiser_form(request, id):
    check_allowed(request, id)
    if request.method == "POST":
        form = AdForm(request.POST, forum_id=id)
        if form.is_valid():
            request.session['session_id'] = form.cleaned_data['session_id']
            request.session['url'] = form.cleaned_data['url']
            request.session['start_url'] = form.cleaned_data['start_url']
            request.session['template'] = form.cleaned_data['template']
            request.session['custom_credentials'] = form.cleaned_data['custom_credentials']
            request.session['custom_username'] = form.cleaned_data['custom_username']
            request.session['custom_password'] = form.cleaned_data['custom_password']
            request.session['forum_id'] = id
            return HttpResponseRedirect(reverse('advertiser:advertiser_process'))
        else:
            print('Something is wrong')
    else:
        active_sessions = BotSession.objects.filter(status='active')
        if len(active_sessions):
            return render(request, "advertiser/stop.html")

        forum = HomeForum.objects.get(pk=id)
        try:
            credentials = CustomCredentials.objects.get(home_forum=id, user=request.user.id)
        except CustomCredentials.DoesNotExist:
            credentials = False

        form = AdForm(initial={
            'session_id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            'url': forum.ad_topic_url,
            'custom_credentials': credentials != False,
            'custom_username': credentials.username if credentials != False else '',
            'custom_password': credentials.password if credentials != False else ''
        }, forum_id=id)
        return render(request, "advertiser/advertiser_form.html", {"form": form, "id": id})

@login_required
def advertiser_process(request):
    forum_id = request.session['forum_id']
    check_allowed(request, forum_id)
    active_sessions = BotSession.objects.filter(status='active')
    if len(active_sessions):
        return render(request, "advertiser/stop.html")

    session_id = request.session['session_id']
    url = request.session['url']
    start_url = request.session['start_url']
    template = request.session['template']
    user_id = request.user.id
    if request.session['custom_credentials']:
        custom_credentials = 'true'
    else:
        custom_credentials = 'false'
    custom_username = request.session['custom_username']
    custom_password = request.session['custom_password']
    # with subprocess.Popen(["python", "advertiser/advertiser_process.py", "-u", data, "symbol"],
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.STDOUT) as process:
    #     for line in process.stdout:
    #         print(line.decode('utf8'))
    subprocess.Popen(["venv/bin/python", "advertiser/advertiser_process.py",
                      "-l", url,
                      "-s", start_url,
                      "-i", session_id,
                      "-t", template,
                      "-c", custom_credentials,
                      "-u", custom_username,
                      "-p", custom_password,
                      '-f', str(forum_id),
                      '-q', str(user_id),
                      "symbol"], stdout=open('subprocess.log', 'a'), stderr=open('subprocess.errlog', 'a'))

    return render(request, "advertiser/advertiser_process.html", {"session_id": session_id})

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
        partners = PartnerTopic.objects.filter(home_forum=id)
        partner_urls = []
        for partner in partners:
            partner_urls.append(partner.url)
        partner_urls = "\n".join(partner_urls)

        form = PartnerForm(initial={
            'session_id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            'urls': partner_urls
        })
        return render(request, "advertiser/partner_form.html", {"form": form, "id": id})

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

    return render(request, "advertiser/partner_process.html", {"session_id": session_id})


@login_required
def forum_edit(request, id):
    check_allowed(request, id)
    if request.method == "POST":
        form = ForumForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            forum = HomeForum.objects.get(pk=id)
            forum.name = form.cleaned_data['name']
            forum.domain = form.cleaned_data['domain']
            forum.ad_topic_url = form.cleaned_data['ad_topic_url']
            forum.save()

            if form.cleaned_data['custom_credentials']:
                try:
                    credentials = CustomCredentials.objects.get(home_forum=forum, user=request.user)
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
                    credentials = CustomCredentials.objects.get(home_forum=forum, user=request.user)
                    credentials.delete()
                except CustomCredentials.DoesNotExist:
                    pass

            partner_urls = form.cleaned_data['partner_urls']
            new_partner_urls = partner_urls.split("\n")
            existing_partners = PartnerTopic.objects.filter(home_forum=id)
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
            credentials = CustomCredentials.objects.get(home_forum=id, user=request.user.id)
        except CustomCredentials.DoesNotExist:
            credentials = False

        partners = PartnerTopic.objects.filter(home_forum=id)
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
            'custom_credentials': credentials != False,
            'custom_username': credentials.username if credentials != False else '',
            'custom_password': credentials.password if credentials != False else '',
        })
        return render(request, "advertiser/forum_form.html", {"form": form, "forum": forum})


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
        templates = AdTemplate.objects.filter(home_forum=id)

        for template in templates:
            template.template_view = 'Coming later'

        form = AdTemplateForm(initial={
            'forum_id': id
        })
        return render(request, "advertiser/ad_templates.html", {"form": form, "templates": templates, "id": id})

@login_required
def delete_template(request, id):
    template = AdTemplate.objects.get(pk=id)
    check_allowed(request, template.home_forum)
    template.delete()
    return HttpResponseRedirect(reverse('advertiser:ad_templates', kwargs={'id': template.home_forum.id}))

@login_required
def history(request, id, page=0):
    forum = HomeForum.objects.get(pk=id)
    check_allowed(request, forum)
    page_size = 50
    sessions = BotSession.objects.filter(home_forum=forum).order_by('-time_start')[page*page_size:(page+1)*page_size]
    return render(request, "advertiser/history.html", {'sessions': sessions})

