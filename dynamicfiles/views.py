import os
import datetime

from django.http import HttpResponse, SimpleCookie
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


def style(request):
    if request.method == "GET":
        path = request.path.split('/')[2]

        filename_prefix = request.COOKIES.get("style_"+path.split('.')[0])
        if filename_prefix is None:
            filename_prefix = "default"

        file = open(os.path.join(BASE_DIR, "dynamicfiles/files", filename_prefix+'_'+path))
        content = file.read()
        response = HttpResponse(content=content, content_type='text/css')
        response['Content-Type'] = 'text/css'
        return response

