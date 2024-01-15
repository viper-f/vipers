from django.db import models


class CrawlSession(models.Model):
    session_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField(default=None, blank=True, null=True)
    folder_path = models.CharField(max_length=100, unique=True)
    visited = models.IntegerField(default=None, blank=True, null=True)
    success = models.IntegerField(default=None, blank=True, null=True)
    stop_signal = models.BooleanField(default=None, blank=True, null=True)
    dead_included = models.BooleanField(default=None, blank=True, null=True)


class Page(models.Model):
    domain = models.CharField(max_length=100, unique=True)
    automatic_page_url = models.CharField(max_length=200, unique=True)
    file_path = models.CharField(max_length=200, unique=True)
    topic_url = models.CharField(max_length=200, unique=True)
    control_session = models.ForeignKey(CrawlSession)
    automatic_result = models.CharField(max_length=100, unique=True)
    corrected_page_url = models.CharField(max_length=200, unique=True)
    verified = models.BooleanField(default=False)


class TrainingSet(models.Model):
    number_of_pages = models.IntegerField()
    number_of_items = models.IntegerField()
    date = models.DateTimeField()
    folder_path = models.CharField(max_length=200, unique=True)


class TrainingSetItem(models.Model):
    training_set = models.ForeignKey(TrainingSet)
    page = models.ForeignKey(Page)
    shuffled = models.BooleanField(default=False)
    input = models.TextField()
    label = models.TextField()
    keys = models.TextField()


class TrainingSession(models.Model):
    time_start = models.DateTimeField()
    time_end = models.DateTimeField(default=None, blank=True, null=True)
    training_set = models.ForeignKey(TrainingSet)
    accuracy = models.FloatField()





