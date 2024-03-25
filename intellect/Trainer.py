# from django.utils import timezone
import os
from random import shuffle
import pickle

import numpy as np
import tensorflow as tf
import keras
from bs4 import BeautifulSoup
from intellect.Intellect import Intellect
from sklearn.model_selection import train_test_split


# from intellect.models import Page, TrainingSet, CrawlSession


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
                path = page.file_path.replace('./pages', self.root_path + '/pages')
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
                for j in range(0, 15):
                    shuffled_datum.append(dataset[i][index * 15 + j])
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

    def train(self, folder_name):
        folder_path = './../training_sets/' + folder_name
        with open(folder_path + '/dataset.pickle', 'rb') as output:
            dataset = pickle.load(output)
        with open(folder_path + '/labels.pickle', 'rb') as output:
            labels = pickle.load(output)

        for i in range(0, 3):
            shuffle_data, shuffle_labels = self.shuffle_dataset(dataset, labels)
            dataset += shuffle_data
            labels += shuffle_labels

        dataset = np.array(dataset)
        labels = np.array(labels)
        training_dataset, test_dataset, training_labels, test_labels = train_test_split(dataset, labels, test_size=0.20, random_state=33)

        model = self.model()
        model.fit(training_dataset, training_labels, epochs=500)
        test_loss, test_acc = model.evaluate(test_dataset, test_labels)
        print('\nTest accuracy: {}'.format(test_acc))
        model.save('./../topic_model_new/model.keras')
      #  tf.keras.models.save_model(model, './../topic_model_new')
       # tf.saved_model.save(model, './../topic_model_new')

    def model(self):
        model = keras.Sequential([
            keras.layers.Dense(150),
           # keras.layers.Dropout(rate=0.3),
            keras.layers.Dense(200),
            keras.layers.Dense(250),
          #  keras.layers.Dropout(rate=0.3),
           # keras.layers.Dropout(rate=0.3),
            keras.layers.Dense(200),
           # keras.layers.Dropout(rate=0.3),
            keras.layers.Dense(150),
           # keras.layers.Dropout(rate=0.3),
            keras.layers.Dense(100),
            #keras.layers.Dropout(rate=0.3),
            keras.layers.Dense(10, activation='softmax'),
        ])
        model.summary()

        initial_learning_rate = 0.001
        lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
            initial_learning_rate,
            decay_steps=1000,
            decay_rate=0.1,
            staircase=True)

        model.compile(optimizer=tf.keras.optimizers.Adam(),
                      loss=tf.keras.losses.CategoricalCrossentropy(),
                      metrics=['accuracy'])
        return model


@tf.function
def custom_metric(y_true, y_pred):
    acc = tf.math.argmax(y_true, axis=1) == tf.math.argmax(y_pred, axis=1)
    elements_equal_to_value = tf.equal(acc, True)
    as_ints = tf.cast(elements_equal_to_value, tf.int32)
    return tf.reduce_sum(as_ints) / tf.size(acc) * 100
