from django.contrib.auth.models import User
from django.db import models


class HomeForum(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    ad_topic_url = models.CharField(max_length=200)
    users = models.ManyToManyField(User, related_name="manager")

    def __str__(self):
        return self.name
