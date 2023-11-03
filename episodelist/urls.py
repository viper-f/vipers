from django.urls import path

from . import views

app_name = 'episodelist'
urlpatterns = [
    path("about", views.about, name="about"),
    path("<int:forum_id>/<str:ids>", views.index, name="index"),
]