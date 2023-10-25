from advertiser.models import HomeForum
from django.core.exceptions import PermissionDenied


def check_allowed(request, home_forum):
        if type(home_forum) is int:
            home_forum = HomeForum.objects.get(pk=home_forum)
        if home_forum.users.filter(id=request.user.id).exists():
            return True
        else:
            raise PermissionDenied
