from django.contrib import admin

from tracker.models import TrackedClick

admin.site.register(TrackedClick)


class TrackedClickAdmin(admin.ModelAdmin):
    search_fields = ['referrer_domain']