from django.urls import path

from . import views

app_name = 'advertiser'
urlpatterns = [
    path("forum-edit/<int:id>", views.forum_edit, name="forum_edit"),
    path("advertiser/<int:id>", views.advertiser_form, name="advertiser_form"),
    path("advertiser-process", views.advertiser_process, name="advertiser_process"),
    path("partner/<int:id>", views.partner_form, name="partner_form"),
    path("partner-process", views.partner_process, name="partner_process"),
]