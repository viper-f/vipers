import os
import datetime

from django.http import HttpResponse, SimpleCookie
from django.views.decorators.clickjacking import xframe_options_exempt

from dynamicfiles.hack import MyMorsel
from vipers.settings import BASE_DIR


@xframe_options_exempt
def set_cookie(request):
    if request.method == "GET":
        cookie = request.GET.get("cookie")
        response = HttpResponse("Yes")

        max_age = 365 * 24 * 60 * 60
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        print(expires)

        m = MyMorsel()
        m["SameSite"] = "None"
        m["Partitioned"] = True
        m["Secure"] = True
        m["Path"] = "/"
        m["expires"] = expires
        m.set("style_filename", cookie, cookie)
        c = SimpleCookie()
        c["style_filename"] = m

        response.cookies["style_filename"] = m

        return response


def style(request):
    if request.method == "GET":
        path = request.path.split('/')[2]

        filename_prefix = request.COOKIES.get('style_filename')
        print(filename_prefix)
        if filename_prefix is None:
            filename_prefix = "old"

        file = open(os.path.join(BASE_DIR, "dynamicfiles/files", filename_prefix+'_'+path))
        content = file.read()
        response = HttpResponse(content=content)
        response['Content-Type'] = 'text/css'
        return response

