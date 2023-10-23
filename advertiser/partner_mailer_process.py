import sys
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import socket
from PartnerMailer import PartnerMailer
from optparse import OptionParser
import json

sys.path.insert(0, './../vipers')
import vipers

parser = OptionParser()
parser.add_option("-u", '--urls', dest="urls")
parser.add_option("-t", '--template', dest="template")
parser.add_option("-i", '--session-id', dest="session_id")
(options, args) = parser.parse_args()

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
print(urls)

mailer.work(
    urls=urls,
    template=options.template,
    custom_login_code=custom_login_code
)

# print('Message sent')

