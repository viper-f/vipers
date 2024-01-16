from django.contrib import admin

from tracker.models import TrackedClick


class TrackedClickAdmin(admin.ModelAdmin):
    search_fields = ['referrer']


admin.site.register(TrackedClick, TrackedClickAdmin)