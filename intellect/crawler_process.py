import sys
from django.utils import timezone

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from Crawler import Crawler
from optparse import OptionParser
import json

from intellect.models import CrawlSession

sys.path.insert(0, './../vipers')
import vipers

import django
django.setup()
from django.contrib.auth.models import User

parser = OptionParser()
parser.add_option("-i", '--session-id', dest="session_id")
parser.add_option("-d", '--dead-included', dest="dead_included")
(options, args) = parser.parse_args()

user = User.objects.get(pk=int(options.user_id))
now = timezone.now()
folder_path = './pages/' + str(options.session_id)
record = CrawlSession(
    session_id=options.session_id,
    status='active',
    time_start=now.isoformat(),
    time_end=None,
    folder_path=folder_path,
    visited=0,
    success=0,
    stop_signal=False,
    dead_included=bool(options.dead_included)
)
record.save()

grop_name = 'comm_' + options.session_id

channel_layer = get_channel_layer()

async_to_sync(channel_layer.group_send)(
    grop_name,
    {
        'type': 'log_message',
        'message': json.dumps({
            "total": 0,
            "visited": 0,
            "success": 0,
            "skipped": 0,
            "message": "Crawler is starting"
        }),
    })


crawler = Crawler(log_mode='channel', channel=channel_layer, session_id=options.session_id, dead_included=bool(options.dead_included))

async_to_sync(channel_layer.group_send)(
    grop_name,
    {
        'type': 'log_message',
        'message': json.dumps({
            "total": 0,
            "visited": 0,
            "success": 0,
            "skipped": 0,
            "message": "Instance created"
        }),
    })

visited, success = crawler.work(options.session_id, folder_path)

now = timezone.now()
record.time_end = now.isoformat()
record.visited = visited
record.success = success
record.status = 'finished'
record.save()

