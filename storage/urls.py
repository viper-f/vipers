from django.urls import path

from . import views

app_name = 'storage'
urlpatterns = [
    path("get", views.record_get, name="get"),
    path("put", views.record_put, name="put")
]