from django.utils import timezone
import os
from random import shuffle
import pickle

import numpy as np
import tensorflow as tf
import keras
from bs4 import BeautifulSoup
from intellect.Intellect import Intellect
from intellect.models import Page, TrainingSet, CrawlSession


class Trainer:
    def __init__(self, root_path=False):
        self.intellect = Intellect()
        if root_path:
            self.root_path = root_path

    def form_dataset(self, crawl_session_id):
        pages = Page.objects.filter(control_session_id=crawl_session_id)
        dataset = []
        labels = []
        for page in pages:
            if self.root_path:
                path = page.file_path.replace('./pages', self.root_path+'/pages')
            else:
                path = page.file_path
            f = open(path, "r", encoding="windows-1251")
            content = f.read()
            data, translation = self.intellect.analize(content, True)

            found, y = False, False
            if page.corrected_topic_id is not None:
                id = page.corrected_topic_id
                found, y = self.find_label(content, id, page.domain)
            if found:
                dataset.append(data)
                labels.append(y)
        return dataset, labels

    def find_label(self, html_text, id, domain):
        url = domain + '/viewtopic.php?id=' + str(id)
        soup = BeautifulSoup(html_text, 'html.parser')
        label_vector = np.zeros(10)
        found = False
        n = 0
        for line in soup.css.select('#pun-main tbody tr'):
            if n >= 10:
                break
            topic = line.css.select('td.tcl a')[0]
            if topic['href'] == url:
                found = True
                label_vector[n] = 1
            n += 1
        return found, label_vector

    def shuffle_dataset(self, dataset, labels):
        indexes = list(range(0, 10))
        shuffle(indexes)
        shuffle_data = []
        shuffle_labels = []
        for i in range(0, len(dataset)):
            shuffled_datum = []
            shuffled_label = []
            for index in indexes:
                for j in range(0, 14):
                    shuffled_datum.append(dataset[i][index+j])
                shuffled_label.append(labels[i][index])
            shuffle_data.append(shuffled_datum)
            shuffle_labels.append(shuffled_label)
        return shuffle_data, shuffle_labels

    def make_training_set(self, crawl_session_id, shuffle_number=3):
        session = CrawlSession.objects.get(pk=crawl_session_id)
        dataset, labels = self.form_dataset(crawl_session_id)
        page_number = len(dataset)

        if shuffle_number:
            shuffled = True
        else:
            shuffled = False

        for i in range(0, shuffle_number):
            shuffle_data, shuffle_labels = self.shuffle_dataset(dataset, labels)
            dataset += shuffle_data
            labels += shuffle_labels

        if self.root_path:
            folder_path = './../training_sets/' + session.session_id
        else:
            folder_path = './training_sets/' + session.session_id
        os.mkdir(folder_path)
        with open(folder_path + '/dataset.pickle', 'wb') as output:
            pickle.dump(dataset, output)
        with open(folder_path + '/labels.pickle', 'wb') as output:
            pickle.dump(labels, output)

        now = timezone.now()
        set = TrainingSet(
            number_of_pages=page_number,
            number_of_items=len(dataset),
            date=now.isoformat(),
            control_session_id=crawl_session_id,
            folder_path=folder_path,
            shuffled=shuffled,
            shuffle_number=shuffle_number
        )
        set.save()

    def train(self, training_set_id):
        set = TrainingSet.objects.get(pk=training_set_id)
        with open(set.folder_path + '/dataset.pickle', 'rb') as output:
            dataset = pickle.load(output)
        with open(set.folder_path + '/labels.pickle', 'rb') as output:
            labels = pickle.load(output)

        index = round(len(dataset) * 0.8)
        training_dataset, test_dataset = dataset[:index], dataset[index:]
        training_labels, test_labels = labels[:index], labels[index:]

        model = self.model()
        model.fit(training_dataset, training_labels, epochs=2000)
        test_loss, test_acc = model.evaluate(test_dataset, test_labels)
        print('\nTest accuracy: {}'.format(test_acc))

    def model(self):
        model = keras.Sequential([
            keras.layers.Dense(name='layer_1', input_shape=(None, 150), units=100),
            keras.layers.Dense(name='layer_2', input_shape=(None, 150), units=100),
            keras.layers.Dense(name='layer_3', input_shape=(None, 100), units=100),
            keras.layers.Dense(name='layer_4', input_shape=(None, 100), units=100),
            keras.layers.Dense(name='layer_5', input_shape=(None, 50), units=100),
            keras.layers.Dense(name='layer_6', input_shape=(None, 50), units=100),
            keras.layers.Dense(name='layer_7', input_shape=(None, 10), units=100),
        ])
        model.summary()

        model.compile(optimizer='adam',
                      loss=tf.keras.losses.MeanAbsoluteError,
                      metrics=[keras.metrics.Accuracy])
        return model
