import pickle
import numpy as np
import requests
from bs4 import BeautifulSoup
import re

def scrape(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    topics = []
    topic_n = 0

    max_message = 0
    authors = {}

    for line in soup.css.select('tbody tr'):

        topic = line.css.select('.tcl .tclcon a')
        if not len(topic):
            continue
        else:
            topic = topic[0]

        topic_n += 1

        last_post = line.css.select('.tcr>a')[0]
        last_poster = line.css.select('.tcr .byuser')[0]
        post_number = line.css.select('.tc2')[0]

        if last_poster.text not in authors:
            authors[last_poster.text] = 0
        authors[last_poster.text] += 1

        topics.append({
            'topic_url': topic['href'],
            'topic_title': topic.text,
            'poster_name': last_poster.text,
            'last_post': last_post.text,
            'last_page_url': last_post['href'],
            'number': topic_n,
            'post_number': int(post_number.text)
        })

        if int(post_number.text) > max_message:
            max_message = int(post_number.text)

        if topic_n > 10:
            break

    max_author = 0
    max_author_name = ''
    for author in authors:
        if authors[author] > max_author:
            max_author = authors[author]
            max_author_name = author


    X = np.zeros(141)

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
        X[i] = int(topic['poster_name'] == max_author)
        i += 1
        X[i] = int(topic['post_number'] == max_message)
        i += 1

    return X, topics


def sigmoid(x):
    s = 1 / (1 + np.exp(-x))
    return s


def relu(x):
    return np.maximum(0, x)


def forward_propagation(X, parameters):
    W1 = parameters["W1"]
    b1 = parameters["b1"]
    W2 = parameters["W2"]
    b2 = parameters["b2"]
    W3 = parameters["W3"]
    b3 = parameters["b3"]

    z1 = np.dot(W1, X) + b1
    a1 = relu(z1)
    z2 = np.dot(W2, a1) + b2
    a2 = relu(z2)
    z3 = np.dot(W3, a2) + b3
    a3 = sigmoid(z3)

    return a3.T


def predict(X, parameters):
    a3 = forward_propagation(X, parameters)
    return np.round(a3)



def get_topic_url(url):
    parameters = pickle.load(open('./advertiser/models/topic_search_model.pickle', 'rb'))
    X, data = scrape(url)
    X = np.reshape(X, (1, 141))
    X = X.T

    prediction = predict(X, parameters)

    topic_url = False
    #topic_title = ''

    for i in range(0, 9):
        if prediction[0][i] and i <= len(data):
            topic_url = data[i - 1]['last_page_url']  # topic numbers start with 1, arrays start with 0
            #topic_title = data[i - 1]['topic_title']
            break

    return topic_url