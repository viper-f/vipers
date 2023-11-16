import os
import sys
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, './../vipers')
import vipers
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vipers.settings")
django.setup()
from advertiser.models import Forum

class ActivityChecker:
    def __init__(self):
        self.forums = self.load_forums()

    def load_forums(self):
        return list(Forum.objects.filter(stop=False).values_list('domain', flat=True))

    def check_activity_24(self, url):
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        try:
            block = soup.css.select('.users_24h')[0]
            number = block.css.select('strong')[0].text
            return number
        except:
            return 'no'

    def work(self):
        for forum in self.forums:
            number = self.check_activity_24(forum)
            print(forum + ' - ' + number)

a = ActivityChecker()
a.work()
