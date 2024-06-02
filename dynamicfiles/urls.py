from django.urls import path, re_path

from . import views

app_name = 'dynamicfiles'
urlpatterns = [
    re_path(r"^[a-zA-Z0-9_]*\.css/$", views.style, name="stype"),
    path("font/style.css", views.style_font, name="font_stype"),
    path("set_cookie", views.set_cookie, name="set_cookie"),
    path("check_cookie_style/<str:cookie_name>", views.check_cookie_style, name="check_cookie_style"),
    path("check_cookie/<str:cookie_name>", views.check_cookie, name="check_cookie"),
]