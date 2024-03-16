import json
import os
from datetime import datetime
import sys
import tensorflow as tf
from asgiref.sync import async_to_sync
import numpy as np
import requests
import re
from requests.exceptions import SSLError
from bs4 import BeautifulSoup

sys.path.insert(0, './../vipers')
import vipers
import django

django.setup()
from advertiser.models import Forum
from intellect.models import Page, CrawlSession
from django.conf import settings


class Crawler:
    def __init__(self, log_mode='console', channel=None, session_id=None, dead_included=False):
        self.links = []
        self.log_mode = log_mode
        self.session_id = session_id
        self.channel = channel
        self.group_name = 'comm_' + session_id
        self.model = tf.keras.models.load_model(str(settings.BASE_DIR) + '/topic_model')
        self.dead_included = dead_included

    def load_from_db(self):
        self.log(total=str(0), success=str(0), skipped=str(0), visited=str(0),
                 message='Loading known data')
        if not self.dead_included:
            forums = Forum.objects.filter(stop=False).order_by("-activity")
        else:
            forums = Forum.objects.all().order_by("-activity")
        for forum in forums:
            self.links.append([forum.domain, forum.verified_forum_id, forum.id])

    def check_stop_signal(self):
        session = CrawlSession.objects.filter(session_id=self.session_id).first()
        if session.stop_signal:
            return True
        else:
            return False

    def get_topic_id(self, url):
        parts_1 = url.split('&p')
        parts_2 = parts_1[0].split('id=')
        parts_3 = parts_2[1].split('#')
        return int(parts_3[0])

    def analize(self, url):
        try:
            html_text = requests.get(url).text
        except SSLError as e:
            url = url.replace('https://', 'http://')
            html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'html.parser')
        topics = []
        topic_n = 0

        max_message = 0
        authors = {}

        X = np.zeros(140)

        for line in soup.css.select('tbody tr'):

            topic = line.css.select('.tcl .tclcon a')
            if not len(topic):
                continue
            else:
                topic = topic[0]

            topic_n += 1

            if len(line.css.select('.tcr>a')):
                last_post = line.css.select('.tcr>a')[0]
                last_poster = line.css.select('.tcr .byuser')[0]
                post_number = line.css.select('.tc2')[0]

                if last_poster.text not in authors:
                    authors[last_poster.text] = 0
                authors[last_poster.text] += 1

                if int(post_number.text) > max_message:
                    max_message = int(post_number.text)

                topics.append({
                    'topic_url': topic['href'],
                    'topic_title': topic.text,
                    'poster_name': last_poster.text,
                    'last_post': last_post.text,
                    'last_page_url': last_post['href'],
                    'number': topic_n,
                    'post_number': int(post_number.text)
                })
            else:
                topics.append({
                    'topic_url': topic['href'],
                    'topic_title': topic.text,
                    'poster_name': '',
                    'last_post': '',
                    'last_page_url': '',
                    'number': topic_n,
                    'post_number': 0
                })

            if topic_n > 9:
                break

        max_author = 0
        max_author_name = ''
        for author in authors:
            if authors[author] > max_author:
                max_author = authors[author]
                max_author_name = author

        i = 0
        for topic in topics:
            X[i] = topic['number'] / topic_n
            i += 1
            X[i] = int('#' in topic['topic_title'].lower())
            i += 1
            X[i] = int('№' in topic['topic_title'].lower())
            i += 1
            X[i] = int(len(re.findall(r'([0-9]*[.]?[0-9])+', topic['topic_title'])) > 0)
            i += 1
            X[i] = int('ваш' in topic['topic_title'].lower())
            i += 1
            X[i] = int('обмен' in topic['topic_title'].lower())
            i += 1
            X[i] = int('реклам' in topic['topic_title'].lower())
            i += 1
            X[i] = int('баннер' in topic['topic_title'].lower())
            i += 1
            X[i] = int('pr' in topic['poster_name'].lower())
            i += 1
            X[i] = int('реклам' in topic['poster_name'].lower())
            i += 1
            X[i] = int('сегодня' in topic['last_post'].lower())
            i += 1
            X[i] = int('вчера' in topic['last_post'].lower())
            i += 1
            X[i] = int(topic['poster_name'] == max_author_name)
            i += 1
            X[i] = int(topic['post_number'] == max_message)
            i += 1

        return X, topics

    def get_topic_url(self, url):
        try:
            X, data = self.analize(url)
        except:
            return False
        prediction = self.model.predict(np.array([X]), verbose=0)
        topic_url = False

        max_v = -1
        max_n = -1

        for i in range(0, 9):
            if prediction[0][i] > max_v:
                max_v = prediction[0][i]
                max_n = i
        try:
            topic_url = data[max_n]['last_page_url']
        except:
            pass
        return topic_url

    def log(self, total, success, skipped, visited, message):
        if self.log_mode == 'console':
            print('Total: ' + total + '; Success: ' + success + '; Message: ' + message)
        if self.log_mode == 'channel':
            async_to_sync(self.channel.group_send)(
                self.group_name,
                {
                    'type': 'log_message',
                    'message': json.dumps({
                        "total": total,
                        "visited": visited,
                        "success": success,
                        "skipped": skipped,
                        "message": message
                    }),
                })

    def download_file(self, folder_path, url, forum_id):
        file_path = folder_path + '/' + str(forum_id) + ".html"
        with open(file_path, "wb") as f:
            r = requests.get(url)
            f.write(r.content)
        return file_path

    def work(self, session_id, folder_path):
        os.mkdir(folder_path)
        print('Starting control at ' + datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        self.load_from_db()
        self.log(total=str(0), success=str(0), skipped=str(0), visited=str(0),
                 message='Starting')

        total = 0
        success = 0
        skipped = 0
        visited = 0

        n = -1

        while n < len(self.links) - 1:

            if self.check_stop_signal():
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Stop signal received')
                break

            n += 1
            visited += 1

            forum_link = self.links[n][0] + '/viewforum.php?id=' + str(self.links[n][1])
            path = self.download_file(folder_path, forum_link, self.links[n][2])
            topic_link = self.get_topic_url(self.links[n][0] + '/viewforum.php?id=' + str(self.links[n][1]))
            if not topic_link:
                skipped += 1
                topic_link = None
                topic_id = None
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Could not find ad topic or load page: ' + self.links[n][0])
            else:
                topic_id = self.get_topic_id(topic_link)

            page = Page(
                domain=self.links[n][0],
                forum_id=self.links[n][2],
                subforum_id=self.links[n][1],
                automatic_topic_url=topic_link,
                automatic_topic_id=topic_id,
                corrected_topic_id=None,
                file_path=path,
                control_session_id=session_id,
                verified=False
            )
            page.save()

        return visited, success
