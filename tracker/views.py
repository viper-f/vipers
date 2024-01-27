import copy
import json
import math
from datetime import datetime, timedelta, timezone

from django.http import HttpResponseRedirect
from django.utils.timezone import make_aware
from django.db import connection
from tracker.models import TrackedClick
from django.shortcuts import render

from tracker.util import check_chart_access, get_hash


def track(request):
    try:
        referrer = request.META['HTTP_REFERER']
    except:
        referrer = ''
    ip = request.META['REMOTE_ADDR']
    client = request.META['HTTP_USER_AGENT']
    try:
        session_id = int(request.GET['id'])
    except:
        session_id = None
    rd = request.GET['rd']
    c = TrackedClick(
        click_time=make_aware(datetime.today()),
        referrer=referrer,
        user_ip=ip,
        user_client=client,
        session_id=session_id
    )
    c.save()
    return HttpResponseRedirect(rd)

def charts(request, id, key=''):
    check_chart_access(request, id, key)
    link = request.build_absolute_uri()
    link += '/' + get_hash(id)
    total = 0
    average_per_run = 0
    max_day = 0
    min_day = 1000



    week_ago = datetime.utcnow() - timedelta(days=7)
    timezone_offset = +3.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    moscow_now = datetime.now(tzinfo)

    # chart 1

    data1 = {
        'labels': [],
        'datasets': [
            {
                'data': [],
            }
        ]
    }

    sql = "SELECT b.time_start at time zone 'Europe/Moscow', COUNT(*) FROM tracker_trackedclick AS t JOIN advertiser_botsession AS b ON b.id = t.session_id AND b.home_forum_id = "+str(id)+" WHERE t.click_time >= TO_DATE('"+week_ago.strftime("%Y-%m-%d %H:%M:%S")+"', '%Y-%m-%d %T') GROUP BY b.id, b.time_start ORDER BY b.time_start ASC"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        db_data = cursor.fetchall()
    for db_datum in db_data:
        data1['labels'].append(db_datum[0].strftime("%Y-%m-%d %H:%M"))
        data1['datasets'][0]['data'].append(db_datum[1])
        total += db_datum[1]
        average_per_run += db_datum[1]

    average_per_run = math.floor(average_per_run / len(data1['labels']))

    # chart 2

    data2 = {
        'labels': [],
        'datasets': []
    }

    print (week_ago.strftime("%Y-%m-%d %H:%M:%S"))

    sql = "SELECT b.id, b.time_start at time zone 'Europe/Moscow', DATE_TRUNC('day', t.click_time at time zone 'Europe/Moscow'), COUNT(*) FROM tracker_trackedclick AS t JOIN advertiser_botsession AS b ON b.id = t.session_id AND b.home_forum_id = "+str(id)+" WHERE t.click_time >= '" + week_ago.strftime(
        "%Y-%m-%d %H:%M:%S") + "' GROUP BY b.id, b.time_start, DATE_TRUNC('day', t.click_time at time zone 'Europe/Moscow') ORDER BY b.time_start ASC"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        db_data = cursor.fetchall()

        print(db_data)

    for i in reversed(range(0, 8)):
        t = moscow_now - timedelta(days=i)
        data2['labels'].append(t.strftime("%Y-%m-%d"))

    n = 0
    indexes = {}

    for db_datum in db_data:
        if db_datum[0] not in indexes:
            indexes[db_datum[0]] = n
            data2['datasets'].append({
                'data': []
            })
            data2['datasets'][n]['label'] = db_datum[1].strftime("%Y-%m-%d %H:%M")
            data2['datasets'][n]['data'] = [0] * 8
            n += 1
        data2['datasets'][indexes[db_datum[0]]]['data'][data2['labels'].index(db_datum[2].strftime("%Y-%m-%d"))] = db_datum[3]
        if (db_datum[3]) < min_day:
            min_day = db_datum[3]
        if (db_datum[3]) > max_day:
            max_day = db_datum[3]


    # chart 4

    data4 = {
        'labels': [],
        'datasets': []
    }

    sql = "SELECT b.id, b.time_start at time zone 'Europe/Moscow', DATE_PART('hour', t.click_time at time zone 'Europe/Moscow'), COUNT(*) FROM tracker_trackedclick AS t JOIN advertiser_botsession AS b ON b.id = t.session_id AND b.home_forum_id = "+str(id)+" WHERE t.click_time >= '" + week_ago.strftime(
        "%Y-%m-%d %H:%M:%S") + "' GROUP BY b.id, b.time_start, DATE_PART('hour', t.click_time at time zone 'Europe/Moscow') ORDER BY b.time_start ASC"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        db_data = cursor.fetchall()

    hours = []
    for i in range(0, 24):
        hours.append(i)
        c = i+1
        if c == 24:
            c = 0
        data4['labels'].append(str(i)+ ':00 - ' + str(c) + ':00')

    n = 0
    indexes = {}

    for db_datum in db_data:
        if db_datum[0] not in indexes:
            indexes[db_datum[0]] = n
            data4['datasets'].append({
                'data': []
            })
            data4['datasets'][n]['label'] = db_datum[1].strftime("%Y-%m-%d %H:%M")
            data4['datasets'][n]['data'] = [0] * 24
            n += 1

        data4['datasets'][indexes[db_datum[0]]]['data'][hours.index(db_datum[2])] = db_datum[3]


    # List

    sql = ("SELECT split_part(RTRIM(referrer, '/'),'/viewtopic', 1) as r, COUNT(*) as c, ROUND(AVG(a.activity), 1) as av FROM tracker_trackedclick AS t "
           "JOIN advertiser_botsession AS b ON b.id = t.session_id AND b.home_forum_id = "+str(id)+" "
           "LEFT JOIN advertiser_forum AS f ON f.domain = split_part(RTRIM(t.referrer, '/'),'?', 1) "
           "LEFT JOIN advertiser_activityrecord AS a ON a.forum_id = f.id AND a.day = DATE(t.click_time) "
           "WHERE t.click_time >= '"
           + week_ago.strftime("%Y-%m-%d %H:%M:%S") + "' GROUP BY r, f.id ORDER BY c DESC")
    # sql = ("SELECT DATE(t.click_time), split_part(RTRIM(referrer, '/'),'/viewtopic', 1) as r, 1 as c, a.activity as av FROM tracker_trackedclick AS t "
    #        "LEFT JOIN advertiser_forum AS f ON f.domain = split_part(RTRIM(t.referrer, '/'),'?', 1) "
    #        "LEFT JOIN advertiser_activityrecord AS a ON a.forum_id = f.id AND a.day = DATE(t.click_time) "
    #        "WHERE t.click_time >= TO_DATE('"
    #        + week_ago.strftime("%Y-%m-%d %H:%M:%S") + "', '%Y-%m-%d %T') ORDER BY c DESC")
    with connection.cursor() as cursor:
        cursor.execute(sql)
        origins = cursor.fetchall()


    return render(request, "tracker/charts.html",
                  {
                      'data1': json.dumps(data1),
                      'data2': json.dumps(data2),
                      'origins': origins,
                      'data4': json.dumps(data4),
                      'link': link,
                      'total': total,
                      'average': average_per_run,
                      'min_day': min_day,
                      'max_day': max_day,
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/tracker/charts", "name": "Трэкинг"},
                      ]
                  })


def modify(request):
    return render(request, "tracker/modify.html",
                  {
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/tracker/modify", "name": "Шаблон для трэкинга"},
                      ]
                  })
