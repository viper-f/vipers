from django.urls import path

from . import views

app_name = 'intellect'
urlpatterns = [
    path("", views.index, name="index"),
    path("crawler-start", views.crawler_form, name="crawler_start"),
    path("crawler-process", views.crawl_process, name="crawler_process"),
    path("session/<int:id>", views.session, name="session"),
    path("page/<int:id>", views.render_page, name="render_page")
]