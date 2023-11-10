from django.urls import path

from . import views

app_name = 'advertiser'
urlpatterns = [
    path("forum-edit/<int:id>", views.forum_edit, name="forum_edit"),
    path("templates/<int:id>", views.ad_templates, name="ad_templates"),
    path("templates/delete/<int:id>", views.delete_template, name="delete_template"),
    path("templates/priority/<int:id>", views.change_priority_template, name="change_priority_template"),
    path("advertiser/<int:id>", views.advertiser_form, name="advertiser_form"),
    path("advertiser-process", views.advertiser_process, name="advertiser_process"),
    path("observe-advertiser-process/<str:session_id>", views.advertiser_process_observe, name="advertiser_process_observe"),
    path("partner/<int:id>", views.partner_form, name="partner_form"),
    path("partner-process", views.partner_process, name="partner_process"),
    path("history/<int:id>", views.history, name="history"),
    path("history/<int:id>/<int:page>", views.history, name="history"),
    path("stop_session/<str:session_id>", views.stop_session, name="stop_session"),
    path("schedule/<int:id>", views.schedule, name="schedule"),
]