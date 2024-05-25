from django.db import models


class StorageRecord(models.Model):
    board_id = models.IntegerField()
    user_id = models.IntegerField(default=None, blank=True, null=True)
    key = models.CharField(max_length=200)
    value = models.TextField()
    type = models.CharField(max_length=10, default="text")
