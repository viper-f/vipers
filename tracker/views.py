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
    domain = referrer.split('/')[0]
    ip = request.META['REMOTE_ADDR']
    client = request.META['HTTP_USER_AGENT']
    try:
        session_id = int(request.GET['id'])
    except:
        session_id = None
    c = TrackedClick(
        click_time=make_aware(datetime.today()),
        referrer_domain=domain,
        referrer=referrer,
        user_ip=ip,
        user_client=client,
        session_id=session_id
    )
    c.save()
    return HttpResponseRedirect('https://kingscross.f-rpg.me')

def charts(request):
    week_ago = datetime.now() - timedelta(days=7)
    data1 = {
        'labels': [],
        'datasets': [
            {
                'data': [],
            }
        ]
    }
    data2 = {
        'labels': [],
        'datasets': []
    }
    now = datetime.now()
    for i in reversed(range(0, 7)):
        t = now - timedelta(days=i)
        data2['labels'].append(t.strftime("%Y-%m-%d"))

    data3 = json.loads(json.dumps(data2))

    sql = "SELECT b.time_start, COUNT(*) FROM tracker_trackedclick AS t JOIN advertiser_botsession AS b ON b.id = t.session_id WHERE t.click_time >= TO_DATE('"+week_ago.strftime("%Y-%m-%d %H:%M:%S")+"', '%Y-%m-%d %T') GROUP BY b.id, b.time_start"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        db_data = cursor.fetchall()
    for db_datum in db_data:
        data1['labels'].append(db_datum[0].strftime("%Y-%m-%d %H:%M"))
        data1['datasets'][0]['data'].append(db_datum[1])

    sql = "SELECT b.id, b.time_start, DATE_TRUNC('day', t.click_time), COUNT(*) FROM tracker_trackedclick AS t JOIN advertiser_botsession AS b ON b.id = t.session_id WHERE t.click_time >= TO_DATE('" + week_ago.strftime(
        "%Y-%m-%d %H:%M:%S") + "', '%Y-%m-%d %T') GROUP BY b.id, b.time_start, DATE_TRUNC('day', t.click_time);"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        db_data = cursor.fetchall()

    n = 0
    indexes = {}

    for db_datum in db_data:
        if db_datum[0] not in indexes:
            print(db_datum[0])
            indexes[db_datum[0]] = n
            data2['datasets'].append({
                'data': []
            })
            data2['datasets'][n]['label'] = db_datum[1].strftime("%Y-%m-%d %H:%M")
            data2['datasets'][n]['data'] = [0] * 7
            n += 1
        data2['datasets'][indexes[db_datum[0]]]['data'][data2['labels'].index(db_datum[2].strftime("%Y-%m-%d"))] = db_datum[3]

    return render(request, "tracker/charts.html",
                  {
                      'data1': json.dumps(data1),
                      'data2': json.dumps(data2),
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/tracker/charts", "name": "Трэкинг"},
                      ]
                  })
