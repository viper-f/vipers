from django.conf import settings


def navigation(request):
    return {
        "is_auth": request.user.is_authenticated
    }