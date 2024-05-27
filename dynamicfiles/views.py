import os
from http.cookiejar import Cookie
from http.cookies import BaseCookie, Morsel
from typing import Mapping, Collection

from django.http import HttpResponse, JsonResponse, SimpleCookie
from django.views.decorators.clickjacking import xframe_options_exempt

from dynamicfiles.hack import MyMorsel
from vipers import settings


@xframe_options_exempt
def set_cookie(request):
    if request.method == "GET":
        cookie = request.GET.get("cookie")
        response = HttpResponse()

        m = MyMorsel()
        m["SameSite"] = "None"
        m["Partitioned"] = True
        m["Secure"] = True
        m["Path"] = "/"
        m.set("style_filename", "red", "red")
        c = SimpleCookie()
        c["style_filename"] = m

        response.cookies["style_filename"] = m

        return response


def style(request):
    if request.method == "GET":

        filename = request.COOKIES.get('style_filename')
        if filename == "red":
            # file = open(os.path.join(settings.ROOT_PATH + "/dynamicfiles/files", 'old.css'))
            # content = file.read()
            content = "body {color: red}"
        else:
            # file = open(os.path.join(settings.ROOT_PATH + "/dynamicfiles/files", 'new.css'))
            # content = file.read()
            content = "body {color: bue}"

        response = HttpResponse(content=content)
        response['Content-Type'] = 'text/css'
        return response

