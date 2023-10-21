import random
import string

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import AdForm, PartnerForm
from django.urls import reverse
import subprocess

def index(request):
    #template = loader.get_template("advertiser/index.html")
    if request.method == "POST":
        form = AdForm(request.POST)
        if form.is_valid():
            request.session['session_id'] = form.cleaned_data['session_id']
            request.session['url'] = form.cleaned_data['url']
            request.session['start_url'] = form.cleaned_data['start_url']
            request.session['template'] = form.cleaned_data['template']
            request.session['custom_credentials'] = form.cleaned_data['custom_credentials']
            request.session['custom_username'] = form.cleaned_data['custom_username']
            request.session['custom_password'] = form.cleaned_data['custom_password']
            return HttpResponseRedirect(reverse('advertiser:process'))
        else:
            print('Something is wrong')
    else:
        form = AdForm(initial={
            'session_id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            'url': 'https://kingscross.f-rpg.me/viewtopic.php?id=6570&p=11',
            'start_url': 'https://kingscross.f-rpg.me/viewtopic.php?id=6570&p=11',
            'template': "[align=center][size=20][font=Impact]A devil family in search of a [url=https://kingscross.f-rpg.me/viewtopic.php?pid=789065#p789065]sister[/url][/font][/size]\n[url=https://kingscross.f-rpg.me/viewtopic.php?pid=789065#p789065][img]https://i.imgur.com/wHedyqx.png[/img][/url]\n[size=20][font=Impact]Scheming, spying, backstabbing, possible incest[/font][/size][/align]",
            'custom_credentials': True,
            'custom_username': 'Assistant'
        })
        return render(request, "advertiser/index.html", {"form": form})


def process(request):
    session_id = request.session['session_id']
    url = request.session['url']
    start_url = request.session['start_url']
    template = request.session['template']
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
                      "symbol"], stdout=open('subprocess.log', 'a'), stderr=open('subprocess.errlog', 'a'))
    template = loader.get_template("advertiser/process.html")
    return HttpResponse(template.render())

def partner_form(request):
    if request.method == "POST":
        form = PartnerForm(request.POST)
        if form.is_valid():
            request.session['session_id'] = form.cleaned_data['session_id']
            request.session['urls'] = form.cleaned_data['urls']
            request.session['template'] = form.cleaned_data['template']
            return HttpResponseRedirect(reverse('advertiser:partner_process'))
        else:
            print('Something is wrong')
    else:
        form = PartnerForm(initial={
            'session_id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        })
        return render(request, "advertiser/partner_form.html", {"form": form})


def partner_process(request):
    session_id = request.session['session_id']
    urls = request.session['url']
    template = request.session['template']
    subprocess.Popen(["venv/bin/python", "advertiser/partner_mailer_process.py",
                      "-u", urls,
                      "-i", session_id,
                      "-t", template,
                      "symbol"], stdout=open('subprocess.log', 'a'), stderr=open('subprocess.errlog', 'a'))
    template = loader.get_template("advertiser/partner_process.html")
    return HttpResponse(template.render())