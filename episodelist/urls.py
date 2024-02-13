from django.urls import path

from . import views

app_name = 'episodelist'
urlpatterns = [
    path("about", views.about, name="about"),
    path("list/<int:forum_id>/<str:ids>", views.index, name="index"),
    path("episodelist/<int:id>", views.episodelist, name="episode_list"),
    path("count/<int:forum_id>/<int:user_id>/<int:time>/<int:before>", views.post_count, name="post_count"),
]