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

class ActivityChecker:
    def __init__(self):
        self.forums = self.load_forums()

    def load_forums(self):
        return list(Forum.objects.exclude(stop=True).values_list('id', 'domain', 'inactive_days', 'board_found'))

    def check_activity_24(self, url):
        try:
            try:
                html = requests.get(url).text
            except ConnectionError as e:
                return 0
        except SSLError as e:
            url = url.replace('https://', 'http://')
            try:
                html = requests.get(url).text
            except ConnectionError as e:
                return 0
        soup = BeautifulSoup(html, 'html.parser')
        try:
            block = soup.css.select('.users_24h')[0]
            number = block.css.select('strong')[0].text
            return int(number)
        except:
            return 0

    def is_forum_dead(self, inactive_days, founded):
        now = time.time()
        if now - founded > 2628000:  # 1 month
            if inactive_days >= 5:
                return 'true'
            else:
                return 'false'
        else:
            if inactive_days >= 15:
                return 'true'
            else:
                return 'false'

    def work(self):
        values = []
        flags = []
        for forum in self.forums:
            number = self.check_activity_24(forum[1])
            if number < 5:
                days = forum[2] + 1
            else:
                days = 0
            is_dead = self.is_forum_dead(days, forum[3])
            values.append('(' + str(number) + ',' + str(days) + ',' + str(forum[0]) + ')')
            flags.append('(' + is_dead + ',' + str(forum[0]) + ')')
        values = ','.join(values)
        flags = ','.join(flags)
        #print("update advertiser_forum as forum set activity = c.activity, inactive_days = c.days, stop = c.is_dead from (values " + values + ") as c(activity, days, is_dead, id) where c.id = forum.id;")

        with connection.cursor() as cursor:
            cursor.execute(
                "update advertiser_forum as forum set activity = c.activity, inactive_days = c.days from (values " + values + ") as c(activity, days, id) where c.id = forum.id;")
            cursor.execute(
                "INSERT INTO advertiser_activityrecord (forum_id, activity, day) SELECT id, activity, CURRENT_DATE FROM advertiser_forum WHERE stop <> TRUE;")
            cursor.execute(
                "update advertiser_forum as forum set stop = c.is_dead from (values " + flags + ") as c(is_dead, id) where c.id = forum.id;")

            connection.commit()

            cursor.close()
            connection.close()
