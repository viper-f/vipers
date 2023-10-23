import sys
from datetime import datetime

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import socket
from PartnerMailer import PartnerMailer
from optparse import OptionParser
import json

sys.path.insert(0, './../vipers')
import vipers

import django
django.setup()
from django.contrib.auth.models import User
from advertiser.models import HomeForum, BotSession, Forum

parser = OptionParser()
parser.add_option("-u", '--urls', dest="urls")
parser.add_option("-t", '--template', dest="template")
parser.add_option("-i", '--session-id', dest="session_id")
parser.add_option("-f", '--forum', dest="forum_id")
parser.add_option("-q", '--username', dest="user_id")
(options, args) = parser.parse_args()

user = User.objects.get(pk=int(options.user_id))
forum = HomeForum.objects.get(pk=int(options.forum_id))
now = datetime.now()
record = BotSession(
    type='partner',
    home_forum=forum,
    user=user,
    session_id=options.session_id,
    status='active',
    time_start=now.isoformat()
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
            "message": "Bot is starting"
        }),
    })

cl_forums = Forum.objects.filter(custom_login__isnull=False)
custom_login_code = {}
for cl_forum in cl_forums:
    custom_login_code[cl_forum.domain] = cl_forum.custom_login

mailer = PartnerMailer(log_mode='channel', channel=channel_layer, group_name=grop_name)

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

urls = options.urls.split("\n")

visited, success = mailer.work(
    urls=urls,
    template=options.template,
    custom_login_code=custom_login_code
)

now = datetime.now()
record.time_end = now.isoformat()
record.visited = visited
record.success = success
record.status = 'finished'
record.save()

