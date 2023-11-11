import string
import random
import sys

from django.contrib.auth.models import User
from django.db import connection
from advertiser.AdvertiserV2 import AdvertiserV2
from advertiser.models import ScheduleItem, BotSession, HomeForum, AdTemplate, Forum
from django.utils import timezone

sys.path.insert(0, './../vipers')
import vipers
sys.path.insert(0, '.')
import advertiser

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
    templates = list(AdTemplate.objects.filter(home_forum=forum.id).order_by("priority").values_list('id', flat=True))

    user = User.objects.get(pk=autorun_id)
    now = timezone.now()
    record = BotSession(
        type='advertiser',
        home_forum=forum,
        user=user,
        session_id=session_id,
        status='active',
        time_start=now.isoformat()
    )
    try:
        record.save()
    except:
        print('This session was already started')
        return False


    cl_forums = Forum.objects.filter(custom_login__isnull=False)
    custom_login_code = {}
    for cl_forum in cl_forums:
        custom_login_code[cl_forum.domain] = cl_forum.custom_login

    stop_list = list(Forum.objects.filter(stop=True).values_list('domain', flat=True))

    advertiser = AdvertiserV2(log_mode='console',  session_id=session_id)


    if custom_credentials == 'true':
        advertiser.custom_login(url=forum.ad_topic_url, username=custom_username,  password=custom_password)

    visited, success, links = advertiser.work(
        url=forum.ad_topic_url,
        home_forum_id=forum.forum.id,
        templates=templates,
        custom_login_code=custom_login_code,
        stop_list=stop_list
    )

    sql_links = []
    if len(links):
        for link in links:
            if link[2] == 'new' and link[1] != 0:
                sql_links.append("('" + link[0] + "'," + str(link[1]) + ")")
        sql_links = ', '.join(sql_links)
        if len(sql_links):
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO advertiser_forum (domain, verified_forum_id) VALUES " + sql_links + " ON CONFLICT DO NOTHING")

    now = timezone.now()
    record.time_end = now.isoformat()
    record.visited = visited
    record.success = success
    record.status = 'finished'
    record.save()

    scheduled_item = now
    scheduled_item.save()




