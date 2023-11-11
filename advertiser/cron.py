import os
import string
import subprocess
import random
import sys

from advertiser.models import ScheduleItem, BotSession, HomeForum, AdTemplate
from django.utils import timezone

def scheduled_bot_run():
    print('schedule 1')
    active_sessions = BotSession.objects.filter(status='active')
    if len(active_sessions):
        print('schedule - another session')
        return False

    now = timezone.now()
    midnight = now.replace(hour=0, minute=0, second=0)

    weekday = now.isoweekday()
    if weekday == 7:
        weekday = 0

    print(now.time().isoformat())
    print(midnight.isoformat())
    print(weekday)

    scheduled_item = ScheduleItem.objects.filter(
        active=True,
        time_start__lte=now.time(),
        last_run__lt=midnight,
        week_day__contains=str(weekday)
    ).first()
    print('schedule 2')

    if scheduled_item is None:
        print('schedule - no item')
        return False

    forum = scheduled_item.home_forum
    cc = scheduled_item.custom_credentials
    if cc is None:
        custom_credentials = False
        custom_username = None
        custom_password = None
    else:
        custom_credentials = True
        custom_username = cc.username
        custom_password = cc.password

    autorun_id = 7
    session_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    url = forum.ad_topic_url
    templates = list(AdTemplate.objects.filter(home_forum=forum.id).order_by("priority").values_list('id', flat=True))
    templates = [str(i) for i in templates]
    print('schedule 3')

    subprocess.Popen(["venv/bin/python", "advertiser/advertiser_process.py",
                      "-l", url,
                      "-i", session_id,
                      "-t", ','.join(templates),
                      "-c", custom_credentials,
                      "-u", custom_username,
                      "-p", custom_password,
                      '-f', str(forum.id),
                      '-q', str(autorun_id),
                      "symbol"], stdout=open('subprocess.log', 'a'), stderr=open('subprocess.errlog', 'a'))


