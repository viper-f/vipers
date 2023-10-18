import sys
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import socket
from selenium import webdriver
from Advertiser import Advertiser
from optparse import OptionParser
import json

sys.path.insert(0, './../vipers')
import vipers

parser = OptionParser()
parser.add_option("-u", '--url', dest="base_url")
parser.add_option("-su", '--start-url', dest="start_url")
parser.add_option("-t", '--template', dest="template")
parser.add_option("-cc", '--custom-credentials', dest="custom_credentials")
parser.add_option("-cu", '--custom-username', dest="custom_username")
parser.add_option("-cp", '--custom-password', dest="custom_password")
(options, args) = parser.parse_args()

channel_layer = get_channel_layer()
group_name = 'test'

stop_list = [
    "https://vampdynasties.mybb.ru",
    "https://curama.mybb.ru",
    "http://curama.mybb.ru",
    "http://themostsupernatural.ru",
    "https://themostsupernatural.ru"
    # "https://faceinless.ru",
    # "https://crossteller.ru",
    # "https://incident.rusff.me",
    # "http://fear.rusff.me/viewtopic.php?id=54&p=9
]

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

advertiser = Advertiser(log_mode='channel', channel=channel_layer, group_name=group_name, data_grab=False)
if options.custom_credentians == 1:
    advertiser.custom_login(url=options.base_url, username=options.custom_username, password=options.custom_password)
advertiser.work(
    url=options.base_url,
    start_url=options.start_url,
    stop_list=stop_list,
    template=options.template,
    custom_login_code=custom_login_code
)

for i in range(20):
    async_to_sync(channel_layer.group_send)(
        'test',
        {
            'type': 'log_message',
            'message': json.dumps({
                "total": (i+10),
                "visited": i,
                "success": (i * 0.7),
                "skipped": (i * 0.3),
                "message": "Now loading http://google.com"
            }),
        })
    time.sleep(2)
# print('Message sent')

