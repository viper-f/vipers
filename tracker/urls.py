from django.urls import path

from . import views

app_name = 'tracker'
urlpatterns = [
    path("track", views.track, name="track"),
    path("charts/<int:id>", views.charts, name="charts"),
    path("charts/<int:id>/<str:key>", views.charts, name="charts_key"),
    path("modify", views.modify, name="modify"),
]