from import_export import resources
from .models import Forum


class ForumResource(resources.ModelResource):
    class Meta:
        model = Forum
