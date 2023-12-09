from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resource import ForumResource

from advertiser.models import Forum, HomeForum, BotSession, ScheduleItem, WantedUpdate, CustomCredentials


class ForumAdmin(ImportExportModelAdmin):
    resource_class = ForumResource


admin.site.register(Forum, ForumAdmin)
admin.site.register(HomeForum)
admin.site.register(BotSession)
admin.site.register(ScheduleItem)
admin.site.register(WantedUpdate)
admin.site.register(CustomCredentials)
