import json
import os
import datetime

from django.http import HttpResponse, SimpleCookie, JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt

from dynamicfiles.hack import MyMorsel
from vipers.settings import BASE_DIR


@xframe_options_exempt
def set_cookie(request):
    if request.method == "GET":
        cookie_name = request.GET.get("cookie_name")
        cookie_value = request.GET.get("cookie_value")
        response = HttpResponse("Yes")

        max_age = 365 * 24 * 60 * 60
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")

        m = MyMorsel()
        m["SameSite"] = "None"
        m["Partitioned"] = True
        m["Secure"] = True
        m["Path"] = "/"
        m["expires"] = expires
        m.set("style_"+cookie_name, cookie_value, cookie_value)
        c = SimpleCookie()
        c["style_"+cookie_name] = m

        response.cookies["style_"+cookie_name] = m
        response.cookies["style_"+cookie_name] = m

        return response

@xframe_options_exempt
def check_cookie(request, cookie_name):
    if request.method == "GET":
        filename_prefix = request.COOKIES.get("style_" + cookie_name)
        if filename_prefix is None:
            filename_prefix = "default_default"
        parts = filename_prefix.split('_')

        response = JsonResponse({"main": parts[0], "contrast": parts[1]})
        response["Access-Control-Allow-Credentials"] = 'true'
        return response


@xframe_options_exempt
def style(request):
    if request.method == "GET":
        path = request.path.split('/')[2]

        filename_prefix = request.COOKIES.get("style_"+path.split('.')[0])
        if filename_prefix is None:
            filename_prefix = "default_default"

        file = open(os.path.join(BASE_DIR, "dynamicfiles/files", filename_prefix+'_'+path))
        content = file.read()
        response = HttpResponse(content=content, content_type='text/css')
        response['Content-Type'] = 'text/css'
        return response

@xframe_options_exempt
def style_font(request):
    if request.method == "GET":

        font = request.COOKIES.get("style_font")
        if font is None:
            content = '/* Nothing to change */'
        else:
            font_parts = font.split(';')
            content = '.post-content p, textarea {font-size: '+font_parts[0]+'px!important; font-family: '+font_parts[1]+'!important}'
        response = HttpResponse(content=content, content_type='text/css')
        response['Content-Type'] = 'text/css'
        return response


