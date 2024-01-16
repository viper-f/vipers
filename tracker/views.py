import copy
import json
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.utils.timezone import make_aware
from django.db import connection
from tracker.models import TrackedClick
from django.shortcuts import render


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
    c = TrackedClick(
        click_time=make_aware(datetime.today()),
        referrer=referrer,
        user_ip=ip,
        user_client=client,
        session_id=session_id
    )
    c.save()
    return HttpResponseRedirect('https://kingscross.f-rpg.me')

def charts(request):
    now = datetime.now()
    week_ago = datetime.now() - timedelta(days=7)

    # chart 1

    data1 = {
        'labels': [],
        'datasets': [
            {
                'data': [],
            }
        ]
    }

    sql = "SELECT b.time_start, COUNT(*) FROM tracker_trackedclick AS t JOIN advertiser_botsession AS b ON b.id = t.session_id WHERE t.click_time >= TO_DATE('"+week_ago.strftime("%Y-%m-%d %H:%M:%S")+"', '%Y-%m-%d %T') GROUP BY b.id, b.time_start"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        db_data = cursor.fetchall()
    for db_datum in db_data:
        data1['labels'].append(db_datum[0].strftime("%Y-%m-%d %H:%M"))
        data1['datasets'][0]['data'].append(db_datum[1])

    # chart 2

    data2 = {
        'labels': [],
        'datasets': []
    }

    sql = "SELECT b.id, b.time_start, DATE_TRUNC('day', t.click_time), COUNT(*) FROM tracker_trackedclick AS t JOIN advertiser_botsession AS b ON b.id = t.session_id WHERE t.click_time >= TO_DATE('" + week_ago.strftime(
        "%Y-%m-%d %H:%M:%S") + "', '%Y-%m-%d %T') GROUP BY b.id, b.time_start, DATE_TRUNC('day', t.click_time);"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        db_data = cursor.fetchall()

    for i in reversed(range(0, 7)):
        t = now - timedelta(days=i)
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
            data2['datasets'][n]['data'] = [0] * 7
            n += 1
        data2['datasets'][indexes[db_datum[0]]]['data'][data2['labels'].index(db_datum[2].strftime("%Y-%m-%d"))] = db_datum[3]

    # chart 3

    data3 = {
        'labels': [],
        'datasets': [
            {
                'data': [],
            }
        ]
    }

    sql = "SELECT referrer, COUNT(*) FROM tracker_trackedclick AS t WHERE t.click_time >= TO_DATE('" + week_ago.strftime(
        "%Y-%m-%d %H:%M:%S") + "', '%Y-%m-%d %T') GROUP BY referrer;"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        db_data = cursor.fetchall()
    for db_datum in db_data:
        if db_datum[0] == '':
            text = 'Unknown'
        else:
            text = db_datum[0]
        data3['labels'].append(text)
        data3['datasets'][0]['data'].append(db_datum[1])


    # chart 4

    data4 = {
        'labels': [],
        'datasets': []
    }

    sql = "SELECT b.id, b.time_start, DATE_PART('hour', t.click_time), COUNT(*) FROM tracker_trackedclick AS t JOIN advertiser_botsession AS b ON b.id = t.session_id WHERE t.click_time >= TO_DATE('" + week_ago.strftime(
        "%Y-%m-%d %H:%M:%S") + "', '%Y-%m-%d %T') GROUP BY b.id, b.time_start, DATE_PART('hour', t.click_time);"
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

        t = int(db_datum[2]) + 3
        if t >= 24:
            t = t - 24
        data4['datasets'][indexes[db_datum[0]]]['data'][hours.index(t)] = db_datum[3]



    return render(request, "tracker/charts.html",
                  {
                      'data1': json.dumps(data1),
                      'data2': json.dumps(data2),
                      'data3': json.dumps(data3),
                      'data4': json.dumps(data4),
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/tracker/charts", "name": "Трэкинг"},
                      ]
                  })
