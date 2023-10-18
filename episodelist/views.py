from django.http import HttpResponse
from django.template import loader
import requests


def index(request, ids):
    base = 'kingscross.f-rpg.me'
    cookie = dict(mybb_ru='MjE4OHwzfDkyOTZmNzM1ZjMxNjliYmM1ZWE4MjhhMTViNjVlNTc3YmViMzNiOTE=')
    url = 'https://'+base+'/api.php?method=users.get&user_id='+ids+'&fields=user_id,username,avatar'
    response = requests.get(url, cookies=cookie)
    data = response.json()
    users = {}
    for user in data['response']['users']:
        users[user['user_id']] = {
            'name': user['username'],
            'avatar': user['avatar']
        }

    url = 'http://'+base+'/api.php?method=board.getSubscriptions&user_id='+ids+'&limit=100'
    response = requests.get(url, cookies=cookie)
    data = response.json()
    processed = []
    episodes = {}
    for datum in data['response']:
        if not datum['topic_id'] in processed:
            episodes[datum['topic_id']] = {
                'url': 'https://'+base+'/viewtopic.php?id='+datum['topic_id'],
                'title': datum['subject'],
                'users': [users[datum['user_id']]]
            }
        else:
            episodes[datum['topic_id']]['users'].append(users[datum['user_id']])
        processed.append(datum['topic_id'])

    template = loader.get_template("episodelist/index.html")
    return HttpResponse(template.render({'episodes': episodes, 'base': base}))
