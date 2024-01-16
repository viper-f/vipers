from django.urls import path

from . import views

app_name = 'tracker'
urlpatterns = [
    path("track", views.track, name="track"),
    path("charts", views.charts, name="charts"),
    path("modify", views.modify, name="modify"),
]