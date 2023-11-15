from django.contrib import admin
from advertiser.models import Forum, HomeForum, BotSession, ScheduleItem, WantedUpdate, CustomCredentials

admin.site.register(Forum)
admin.site.register(HomeForum)
admin.site.register(BotSession)
admin.site.register(ScheduleItem)
admin.site.register(WantedUpdate)
admin.site.register(CustomCredentials)