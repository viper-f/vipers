from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import subprocess
import sys
import requests


def index(request):
    # with subprocess.Popen(["python", "advertiser/advertiser_process.py", "symbol"],
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.STDOUT) as process:
    #     for line in process.stdout:
    #         print(line.decode('utf8'))
    subprocess.Popen(["python", "advertiser/advertiser_process.py", "symbol"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    template = loader.get_template("advertiser/index.html")
    return HttpResponse(template.render())


