import sys
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import socket
from PartnerMailer import PartnerMailer
from optparse import OptionParser
import json

sys.path.insert(0, '..')
import vipers

channel_layer = get_channel_layer()
group_name = 'test'


async_to_sync(channel_layer.group_send)(
    'test',
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


parser = OptionParser()
parser.add_option("-u", '--urls', dest="urls")
parser.add_option("-t", '--template', dest="template")
(options, args) = parser.parse_args()

async_to_sync(channel_layer.group_send)(
    'test',
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
    "https://daas.rusff.me": "PR['in_2']()"
}

mailer = PartnerMailer(log_mode='channel', channel=channel_layer, group_name=group_name)

async_to_sync(channel_layer.group_send)(
    'partner',
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


mailer.work(
    urls=options.urls,
    template=options.template,
    custom_login_code=custom_login_code
)

# print('Message sent')

