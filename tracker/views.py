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
    data = {
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
        data['labels'].append(db_datum[0].strftime("%Y-%m-%d %H:%M"))
        data['datasets'][0]['data'].append(db_datum[1])

    return render(request, "tracker/charts.html",
                  {
                      'data1': json.dumps(data),
                      "breadcrumbs": [
                          {"link": "/", "name": "Главная"},
                          {"link": "/tracker/charts", "name": "Трэкинг"},
                      ]
                  })
