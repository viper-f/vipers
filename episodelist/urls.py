from django.urls import path

from . import views

app_name = 'episodelist'
urlpatterns = [
    path("about", views.about, name="about"),
    path("<str:ids>", views.index, name="index"),
]