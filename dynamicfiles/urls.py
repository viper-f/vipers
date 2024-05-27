from django.urls import path

from . import views

app_name = 'dynamicfiles'
urlpatterns = [
    path("style.css", views.style, name="stype"),
    path("set_cookie", views.set_cookie, name="set_cookie"),
]