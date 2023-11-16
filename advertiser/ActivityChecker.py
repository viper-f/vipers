import os
import sys
import requests
from bs4 import BeautifulSoup

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
        return list(Forum.objects.filter(stop=False).values_list('id', 'domain'))

    def check_activity_24(self, url):
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        try:
            block = soup.css.select('.users_24h')[0]
            number = block.css.select('strong')[0].text
            return number
        except:
            return 'null'

    def work(self):
        values = []
        for forum in self.forums:
            number = self.check_activity_24(forum['domain'])
            print(forum + ' - ' + number)
            values.append('(' + number + ',' + str(forum['id']) + ')')
        values = ','.join(values)
        with connection.cursor() as cursor:
            cursor.execute(
                "update advertiser_forum as forum set activity = c.column_a from (values " + values + ") as c(column_a, column_b) where c.column_b = forum.id;")


a = ActivityChecker()
a.work()
