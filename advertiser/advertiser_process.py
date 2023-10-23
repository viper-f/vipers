import sys
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import socket
from datetime import datetime
from Advertiser import Advertiser
from optparse import OptionParser
import json

sys.path.insert(0, './../vipers')
import vipers

import django
django.setup()
from django.contrib.auth.models import User
from advertiser.models import HomeForum, BotSession


parser = OptionParser()
parser.add_option("-l", '--url', dest="base_url")
parser.add_option("-s", '--start-url', dest="start_url")
parser.add_option("-t", '--template', dest="template")
parser.add_option("-i", '--session-id', dest="session_id")
parser.add_option("-c", '--custom-credentials', dest="custom_credentials")
parser.add_option("-u", '--custom-username', dest="custom_username")
parser.add_option("-p", '--custom-password', dest="custom_password")
parser.add_option("-f", '--username', dest="user_id")
parser.add_option("-q", '--forum', dest="forum_id")
(options, args) = parser.parse_args()

user = User.objects.get(pk=int(options.user_id))
forum = HomeForum.objects.get(pk=int(options.forum_id))
now = datetime.now()
record = BotSession(
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




async_to_sync(channel_layer.group_send)(
    grop_name,
    {
        'type': 'log_message',
        'message': json.dumps({
            "total": 0,
            "visited": 0,
            "success": 0,
            "skipped": 0,
            "message": "Parameters read"
        }),
    })


# stop_list = [
#     # "https://vampdynasties.mybb.ru",
#     # "https://curama.mybb.ru",
#     # "http://curama.mybb.ru",
#     "http://themostsupernatural.ru",
#     "https://themostsupernatural.ru",
#     # "https://grishaversesab.ru"
#     # "https://faceinless.ru",
#     # "https://crossteller.ru",
#     # "https://incident.rusff.me",
#     # "http://fear.rusff.me/viewtopic.php?id=54&p=9
# ]

custom_login_code = {
    "https://phoenixlament.f-rpg.me": "PiarIn()",
    "https://execute.rusff.me": "PR['in_2']()",
    "https://intovoid.f-rpg.me": "PR['in_2']()",
    "https://sacramento.rusff.me": "PrLogin('pr')",
    "https://asphodel.rusff.me": "PR['in_2']()",
    "https://timess.rusff.me": "PR['in_2']()",
    "https://verbaveritatis.rusff.me": "PR['in_2']()",
    "https://miyron.rolka.me": "PiarIn(PiarNik1,PiarPas1)",
    "https://drinkbutterbeer.ru": "PrLogin('pr')",
    "https://dragonageone.mybb.ru": "PR['in_2']()",
    "https://toeden.rusff.me": "PR['in_2']()",
    "https://kakbicross.ru": "PR['in_2']()",
    "https://daas.rusff.me": "PR['in_2']()",
    "https://hornyjail.ru": "PR['in_2']()",
    "https://rains.rusff.me": "PrLogin('pr')",
    "https://docnight.rusff.me": "PR['in_2']()"
}

advertiser = Advertiser(log_mode='channel', channel=channel_layer, group_name=grop_name, data_grab=False)

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

visited, success = advertiser.work(
    url=options.base_url,
    start_url=options.start_url,
    template=options.template,
    custom_login_code=custom_login_code
)

now = datetime.now()
record.time_end = now.isoformat()
record.visited = visited
record.success = success
record.status = 'finished'
record.save()

