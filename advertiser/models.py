from django.contrib.auth.models import User
from django.db import models


class Forum(models.Model):
    domain = models.CharField(max_length=100, unique=True)
    custom_login = models.CharField(max_length=200, default=None, blank=True, null=True)
    stop = models.BooleanField(default=None, blank=True, null=True)
    type = models.CharField(max_length=100, default=None, blank=True, null=True)
    predicted_forum_id = models.IntegerField(default=None, blank=True, null=True)
    predicted_topic_name = models.CharField(max_length=200, default=None, blank=True, null=True)
    prediction_date = models.DateTimeField(default=None, blank=True, null=True)
    verified_forum_id = models.IntegerField(default=None, blank=True, null=True)
    verified_topic_name = models.CharField(max_length=200, default=None, blank=True, null=True)
    verification_date = models.DateTimeField(default=None, blank=True, null=True)
    activity = models.IntegerField(default=None, blank=True, null=True)
    inactive_days = models.IntegerField(default=0)
    board_id = models.CharField(max_length=10, default=None, blank=True, null=True)

    def __str__(self):
        return self.domain

class HomeForum(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True)
    ad_topic_url = models.CharField(max_length=200)
    users = models.ManyToManyField(User, related_name="manager")
    forum = models.ForeignKey(Forum, on_delete=models.DO_NOTHING, default=None, blank=True, null=True)

    def __str__(self):
        return self.name


class PartnerTopic(models.Model):
    url = models.CharField(max_length=200)
    home_forum = models.ForeignKey(HomeForum, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, default='partner')


class CustomCredentials(models.Model):
    home_forum = models.ForeignKey(HomeForum, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    type = models.CharField(max_length=10, default='home')


class AdTemplate(models.Model):
    home_forum = models.ForeignKey(HomeForum, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.TextField()
    priority = models.IntegerField(default=None, blank=True, null=True)


class BotSession(models.Model):
    type = models.CharField(max_length=20, default='advertiser')
    home_forum = models.ForeignKey(HomeForum, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField(default=None, blank=True, null=True)
    visited = models.IntegerField(default=None, blank=True, null=True)
    success = models.IntegerField(default=None, blank=True, null=True)
    stop_signal = models.BooleanField(default=None, blank=True, null=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session_id"],
                name="unique_session_id"
            )
        ]

class ScheduleItem(models.Model):
    home_forum = models.ForeignKey(HomeForum, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, default='ad')
    week_day = models.CharField(max_length=7)
    time_start = models.TimeField()
    custom_credentials = models.ForeignKey(CustomCredentials, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=True)
    last_run = models.DateTimeField()


class WantedUpdate(models.Model):
    donor_url = models.CharField(max_length=200)
    target_url = models.CharField(max_length=200)
    home_forum = models.ForeignKey(HomeForum, on_delete=models.CASCADE)
    target_post_id = models.IntegerField(default=None, blank=True, null=True)
    custom_credentials = models.ForeignKey(CustomCredentials, default=None, blank=True, null=True, on_delete=models.SET_NULL)