from django.contrib.auth.models import User
from django.db import models


class EpisodeListSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=200)
    cookie = models.CharField(max_length=200)
