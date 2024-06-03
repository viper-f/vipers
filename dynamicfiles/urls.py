from django.urls import path

from . import views

app_name = 'dynamicfiles'
urlpatterns = [
    path("style.css", views.style, name="style"),
    path("mobile.css", views.mobile, name="mobile"),
    path("font/style.css", views.style_font, name="font_stype"),
    path("set_cookie", views.set_cookie, name="set_cookie"),
    path("check_cookie_style/<str:cookie_name>", views.check_cookie_style, name="check_cookie_style"),
    path("check_cookie/<str:cookie_name>", views.check_cookie, name="check_cookie"),
]