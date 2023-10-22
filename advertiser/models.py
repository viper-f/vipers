from django.contrib.auth.models import User
from django.db import models


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