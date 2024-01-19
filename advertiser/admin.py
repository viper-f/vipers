from django.contrib import admin
from advertiser.models import Forum, HomeForum, BotSession, ScheduleItem, WantedUpdate, CustomCredentials, \
    ActivityRecord

admin.site.register(BotSession)
admin.site.register(ScheduleItem)
admin.site.register(WantedUpdate)
admin.site.register(CustomCredentials)
admin.site.register(ActivityRecord)

class ForumAdmin(admin.ModelAdmin):
    search_fields = ['domain']


class HomeForumAdmin(admin.ModelAdmin):
    autocomplete_fields = ['forum']


admin.site.register(Forum, ForumAdmin)
admin.site.register(HomeForum, HomeForumAdmin)
