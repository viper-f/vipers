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
    path("correct/<int:page_id>/<str:topic_url>", views.correct_id, name="correct_id"),
    path("dataset/generate/<int:id>", views.dataset_generate, name="dataset_generate")
]