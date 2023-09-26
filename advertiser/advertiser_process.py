import sys
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import socket
from selenium import webdriver
from Advertiser import Advertiser
from optparse import OptionParser

sys.path.insert(0, './../vipers')
import vipers

parser = OptionParser()
parser.add_option("-u", '--url', dest="base_url")
(options, args) = parser.parse_args()

channel_layer = get_channel_layer()
group_name = 'test'

# advertiser = Advertiser(log_mode='channel', channel=channel_layer, group_name=group_name)
# advertiser.work(options.base_url)

for i in range(20):
    async_to_sync(channel_layer.group_send)(
        'test',
        {
            'type': 'chat_message',
            'message': 'Some line of text',
        })
    time.sleep(2)
# print('Message sent')

