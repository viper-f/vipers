from django.http import HttpResponse
from django.template import loader
import requests
from django.shortcuts import render

from episodelist.models import EpisodeListSettings


def index(request, forum_id, ids):
    settings = EpisodeListSettings.objects.get(pk=forum_id)
    if not settings:
        raise Exception('This forum does not exist')
    base = settings.url
    cookie = dict(mybb_ru=settings.cookie)
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

def about(request):
    code = '<div id="list"></div>\n<script>\nlet url = "https://viper-frpg.ovh/episodelist/2/2202,2180,2196,2189,2184,2224,2209,2190,2186,2234,2195,2201,2188,2181";\nfetch(url, {\n    method: "GET" \n})\n    .then((response) => {\n        if (!response.ok) {\n            throw Error(response.statusText);\n        }\n        return response.text();\n    })\n    .then((html) => {\n        document.getElementById("list").innerHTML = html;\n    })\n.catch((error) => {\n    console.error(error);\n});\n</script>'
    return render(request, "episodelist/about.html", {"code": code})
