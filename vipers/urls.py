"""
URL configuration for vipers project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("user-index", views.user_index, name="user_index"),
    path("user-settings", views.user_settings, name="user_settings"),
    path("episodelist/", include("episodelist.urls")),
    path("episodemover/", include("episodemover.urls")),
    path("scripts/", include("scripts.urls")),
    path("tracker/", include("tracker.urls")),
    path("advertiser/", include("advertiser.urls")),
    path("intellect/", include("intellect.urls")),
    path("storage/", include("storage.urls")),
    path('admin/', admin.site.urls),
    path("select2/", include("django_select2.urls")),
    path("dynamicfiles/", include("dynamicfiles.urls"))
]
