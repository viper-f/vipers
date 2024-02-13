from django.contrib.auth.models import User
from django.db import models


class EpisodeListSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=200)
    cookie = models.CharField(max_length=200)
    hash = models.CharField(max_length=200)

class Category(models.Model):
    title = models.CharField(max_length=200)
    weight = models.IntegerField(default=None, blank=True, null=True)
    is_default = models.BooleanField(default=False)

class Episode(models.Model):
    list = models.ForeignKey(EpisodeListSettings, on_delete=models.CASCADE)
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    forum_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, default=None, blank=True, null=True, on_delete=models.DO_NOTHING)
    weight = models.IntegerField(default=None, blank=True, null=True)

class EpisodeCharacters(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    character_id = models.IntegerField()
    character_name = models.CharField(max_length=200)
    avatar_url = models.CharField(max_length=200, default=None, blank=True, null=True)