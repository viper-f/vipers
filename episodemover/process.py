import sys
from optparse import OptionParser

from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from EpisodeMover import EpisodeMover
import json

sys.path.insert(0, './../vipers')
import vipers

import django
django.setup()

parser = OptionParser()
parser.add_option("-j", '--json', dest="json")
(options, args) = parser.parse_args()

j = options.json

print('Moving episode')
print(j)
data = json.dumps(j)

now = timezone.now()

grop_name = 'comm_' + data['session_id']

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
            "message": "Moving is starting"
        }),
    })


mover = EpisodeMover(log_mode='channel', channel=channel_layer, session_id=data['session_id'])

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

mover.work(data['old_episode'], data['new_episode'], data['characters'])

