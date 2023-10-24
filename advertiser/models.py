from django.contrib.auth.models import User
from django.db import models


class Forum(models.Model):
    domain = models.CharField(max_length=100)
    custom_login = models.CharField(max_length=200, default=None, blank=True, null=True)
    stop = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.domain

class HomeForum(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    ad_topic_url = models.CharField(max_length=200)
    users = models.ManyToManyField(User, related_name="manager")

    def __str__(self):
        return self.name


class PartnerTopic(models.Model):
    url = models.CharField(max_length=200)
    home_forum = models.ForeignKey(HomeForum, on_delete=models.CASCADE)


class CustomCredentials(models.Model):
    home_forum = models.ForeignKey(HomeForum, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=200)


class AdTemplate(models.Model):
    home_forum = models.ForeignKey(HomeForum, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.TextField()


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

