from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import UrlForm
from django.urls import reverse
import subprocess
import sys
import requests


def index(request):
    #template = loader.get_template("advertiser/index.html")
    if request.method == "POST":
        form = UrlForm(request.POST)
        if form.is_valid():
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
        form = UrlForm
        return render(request, "advertiser/index.html", {"form": form})


def process(request):
    url = request.session['url']
    start_url = request.session['start_url']
    template = request.session['template']
    custom_credentials = request.session['custom_credentials']
    custom_username = request.session['custom_username']
    custom_password = request.session['custom_password']
    # with subprocess.Popen(["python", "advertiser/advertiser_process.py", "-u", data, "symbol"],
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.STDOUT) as process:
    #     for line in process.stdout:
    #         print(line.decode('utf8'))
    subprocess.Popen(["python", "advertiser/advertiser_process.py",
                      "-u", url,
                      "-su", start_url,
                      "-t", template,
                      "-cc", custom_credentials,
                      "-cu", custom_username,
                      "-cp", custom_password,
                      "symbol"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    template = loader.get_template("advertiser/process.html")
    return HttpResponse(template.render())
