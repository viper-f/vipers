from django.urls import path

from . import views

app_name = 'intellect'
urlpatterns = [
    path("", views.index, name="index"),
    path("crawler-start", views.crawler_form, name="crawler_start"),
    path("crawler-process", views.crawl_process, name="crawler_process"),
    path("session/<int:id>", views.session, name="session"),
    path("page_redirect/<int:id>", views.render_page_redirect, name="render_page_redirect"),
    path("page/<int:id>", views.render_page, name="render_page"),
    path("verify/<int:id>", views.verify, name="verify"),
    path("correct/<int:page_id>/<int:topic_id>", views.correct_id, name="correct_id"),
    path("download/<int:id>/<str:filename>", views.download_training_set, name="download")
]