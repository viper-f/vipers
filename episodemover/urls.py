from django.urls import path

from . import views

app_name = 'episodemover'
urlpatterns = [
    path("index", views.index, name="index"),
    path("process", views.process, name="process"),
]