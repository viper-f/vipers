from django.urls import path

from . import views

urlpatterns = [
    path("<str:ids>", views.index, name="index"),
]