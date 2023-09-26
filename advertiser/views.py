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
            return HttpResponseRedirect(reverse('advertiser:process'))
        else:
            print('Something is wrong')
    else:
        form = UrlForm
        return render(request, "advertiser/index.html", {"form": form})


def process(request):
    data = request.session['url']
    # with subprocess.Popen(["python", "advertiser/advertiser_process.py", "-u", data, "symbol"],
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.STDOUT) as process:
    #     for line in process.stdout:
    #         print(line.decode('utf8'))
    subprocess.Popen(["python", "advertiser/advertiser_process.py", "-u", data, "symbol"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    template = loader.get_template("advertiser/process.html")
    return HttpResponse(template.render())
