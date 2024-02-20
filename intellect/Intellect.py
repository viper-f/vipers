import numpy as np
import requests
import re
from requests.exceptions import SSLError
from bs4 import BeautifulSoup
class Intellect:

    def analize(self, url, file=False):
        if file:
            html_text = url
        else:
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