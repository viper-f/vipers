import json
import os
import sys
import time

import requests
from bs4 import BeautifulSoup
from requests.exceptions import SSLError

sys.path.insert(0, './../vipers')
import vipers
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vipers.settings")
django.setup()
from django.db import connection
from advertiser.models import Forum

class AddId:
    def __init__(self):
        self.forums = self.load_forums()

    def load_forums(self):
        return list(Forum.objects.all().values_list('id', 'domain'))

    def get_id(self, url):
        url += '/api.php?method=board.get'
        try:
            text = requests.get(url).text
        except SSLError as e:
            url = url.replace('https://', 'http://')
            text = requests.get(url).text
        data = json.loads(text)
        return data['response']['board_id'], data['response']['found']


    def work(self):
        values = []
        for forum in self.forums:
            board_id, found = self.get_id(forum[1])
            values.append("('" + board_id + "'," + found + "," + str(forum[0]) + ')')
        values = ','.join(values)
        with connection.cursor() as cursor:
            cursor.execute(
                "update advertiser_forum as forum set board_id = c.board_id, board_found = c.found from (values " + values + ") as c(board_id, found, id) where c.id = forum.id;")

a = AddId()
a.work()