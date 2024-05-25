from django.contrib import admin
from storage.models import StorageForum, StorageRecord

admin.site.register(StorageRecord)
admin.site.register(StorageForum)
