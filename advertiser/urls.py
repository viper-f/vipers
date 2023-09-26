from django.urls import path

from . import views

app_name = 'advertiser'
urlpatterns = [
    path("", views.index, name="index"),
    path("process", views.process, name="process"),
]