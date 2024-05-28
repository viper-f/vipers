from django.urls import path, re_path

from . import views

app_name = 'dynamicfiles'
urlpatterns = [
    re_path(r"^[a-zA-Z0-9_]*\.css/$", views.style, name="stype"),
    path("set_cookie", views.set_cookie, name="set_cookie"),
]