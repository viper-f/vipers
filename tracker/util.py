from django.core.exceptions import PermissionDenied
from django.http import Http404

from advertiser.models import HomeForum
import hashlib


def check_chart_access(request, home_forum, key):
    if type(home_forum) is int:
        home_forum = HomeForum.objects.get(pk=home_forum)
    if home_forum is None:
        raise Http404

    if request.user is not None and home_forum.users.filter(id=request.user.id).exists():
        return True
    if key == hashlib.sha256(
            home_forum.domain.encode("utf-8") + str(home_forum.forum.id).encode("utf-8") + str(home_forum.forum.verified_forum_id).encode("utf-8")).hexdigest():
        return True

    raise PermissionDenied


def get_hash(home_forum):
    if type(home_forum) is int:
        home_forum = HomeForum.objects.get(pk=home_forum)
    return hashlib.sha256(
        home_forum.domain.encode("utf-8") + str(home_forum.forum.id).encode("utf-8") + str(home_forum.forum.verified_forum_id).encode("utf-8")).hexdigest()
