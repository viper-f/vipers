import sys
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import socket
from selenium import webdriver
from Advertiser import Advertiser

sys.path.insert(0, './../vipers')
import vipers



time.sleep(2)
advertiser = Advertiser()
links = advertiser.scrape_links("https://kingscross.f-rpg.me/viewtopic.php?id=6471&p=42#p788489")


channel_layer = get_channel_layer()
#message(channel_layer)
async_to_sync(channel_layer.group_send)(
    'test',
    {
        'type': 'chat_message',
        'message': str(links),
    })
print('Message sent')

