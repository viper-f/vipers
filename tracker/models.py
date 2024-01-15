from django.db import models

import advertiser.models


class TrackedClick(models.Model):
    click_time = models.DateTimeField()
    referrer_domain = models.CharField(max_length=200)
    referrer = models.CharField(max_length=200)
    user_ip = models.CharField(max_length=50, default=None, blank=True, null=True)
    user_client = models.CharField(max_length=300, default=None, blank=True, null=True)
    session = models.ForeignKey(advertiser.models.BotSession, default=None, blank=True, null=True, on_delete=models.DO_NOTHING)



