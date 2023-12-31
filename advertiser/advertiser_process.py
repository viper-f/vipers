import sys
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from selenium.common import NoSuchDriverException

from AdvertiserV2 import AdvertiserV2
from AdvertiserV2Rusff import AdvertiserV2Rusff
from optparse import OptionParser
import json

sys.path.insert(0, './../vipers')
import vipers

import django

django.setup()
from django.db import connection
from django.contrib.auth.models import User
from advertiser.models import HomeForum, BotSession, Forum

parser = OptionParser()
parser.add_option("-l", '--url', dest="base_url")
parser.add_option("-t", '--templates', dest="templates")
parser.add_option("-i", '--session-id', dest="session_id")
parser.add_option("-c", '--custom-credentials', dest="custom_credentials")
parser.add_option("-u", '--custom-username', dest="custom_username")
parser.add_option("-p", '--custom-password', dest="custom_password")
parser.add_option("-f", '--forum', dest="forum_id")
parser.add_option("-q", '--username', dest="user_id")
(options, args) = parser.parse_args()

templates = options.templates.split(',')
templates = [int(i) for i in templates]

user = User.objects.get(pk=int(options.user_id))
forum = HomeForum.objects.get(pk=int(options.forum_id))
now = timezone.now()
record = BotSession(
    type='advertiser',
    home_forum=forum,
    user=user,
    session_id=options.session_id,
    status='active',
    time_start=now.isoformat()
)
try:
    record.save()
except:
    print('This session was already started')
    exit(0)

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

stop_list = list(Forum.objects.filter(stop=True).values_list('domain', flat=True))

if options.custom_credentials == 'true':
    user_dir = "/home/root/vipers/profile-"+str(forum.forum.id)+"-"+options.custom_username
else:
    user_dir = "/home/root/vipers/profile"

try:
    if forum.is_rusff:
        advertiser = AdvertiserV2Rusff(user_dir=user_dir, log_mode='channel', channel=channel_layer, session_id=options.session_id)
    else:
        advertiser = AdvertiserV2(user_dir=user_dir, log_mode='channel', channel=channel_layer, session_id=options.session_id)

except NoSuchDriverException:
    now = timezone.now()
    record.time_end = now.isoformat()
    record.visited = 0
    record.success = 0
    record.status = 'finished'
    record.save()
    async_to_sync(channel_layer.group_send)(
        grop_name,
        {
            'type': 'log_message',
            'message': json.dumps({
                "total": 0,
                "visited": 0,
                "success": 0,
                "skipped": 0,
                "message": "Browser could not start. Shutting down. Please retry"
            }),
        })
    exit(0)

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

if options.custom_credentials == 'true':
    async_to_sync(channel_layer.group_send)(
        grop_name,
        {
            'type': 'log_message',
            'message': json.dumps({
                "total": 0,
                "visited": 0,
                "success": 0,
                "skipped": 0,
                "message": "Attempting custom login"
            }),
        })
    advertiser.custom_login(url=options.base_url, username=options.custom_username, password=options.custom_password)

visited, success, links = advertiser.work(
    url=options.base_url,
    id=forum.id,
    home_forum_id=forum.forum.id,
    templates=templates,
    custom_login_code=custom_login_code,
    stop_list=stop_list
)

now = timezone.now()
record.time_end = now.isoformat()
record.visited = visited
record.success = success
record.status = 'finished'
record.save()

sql_links = []
if len(links):
    for link in links:
        if link[2] == 'new' and link[1] != 0:
            print("('" + link[0] + "'," + str(link[1]) + ",'" + link[3] + "'," + link[4] + ")")
            sql_links.append("('" + link[0] + "'," + str(link[1]) + ",'" + link[3] + "'," + link[4] + ",0)")
    sql_links = ', '.join(sql_links)
    if len(sql_links):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO advertiser_forum (domain, verified_forum_id, board_id, board_found, inactive_days) VALUES " + sql_links + " ON CONFLICT DO NOTHING")
            connection.commit()