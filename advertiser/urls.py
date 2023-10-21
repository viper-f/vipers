from django.urls import path

from . import views

app_name = 'advertiser'
urlpatterns = [
    path("", views.index, name="index"),
    path("process", views.process, name="process"),
    path("partner", views.partner_form, name="partner_form"),
    path("partner-process", views.partner_process, name="partner_process"),
]