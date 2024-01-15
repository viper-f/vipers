from requests.exceptions import SSLError
from selenium import webdriver
from selenium.common import NoSuchDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
from asgiref.sync import async_to_sync
import json
from datetime import datetime
import sys
import tensorflow as tf
import numpy as np
import requests
from bs4 import BeautifulSoup

from advertiser.AdvertiserV2 import AdvertiserV2

sys.path.insert(0, './../vipers')
import vipers
import django
django.setup()
from advertiser.models import Forum, BotSession, AdTemplate, HomeForum
from django.conf import settings


class Crawler (AdvertiserV2):
    def __init__(self, user_dir="/home/root/vipers/profile", log_mode='console', channel=None, session_id=None):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.page_load_strategy = 'eager'
        self.links = []
        self.tracked = []
        self.tracked_id = []
        self.log_mode = log_mode
        self.session_id = session_id
        self.channel = channel
        self.group_name = 'comm_' + session_id
        self.home_base = ''
        self.logged_in = False
        self.custom_l = False
        self.model = tf.keras.models.load_model(str(settings.BASE_DIR)+'/topic_model')
        self.templates = []
        self.forum_settings = {}

        options.add_argument("user-data-dir=" + user_dir)
        self.driver1 = webdriver.Chrome(options=options)
        options.add_argument("user-data-dir=/home/root/vipers/profile")
        self.driver2 = webdriver.Chrome(options=options)



    def load_from_db(self, home_forum_id):
        self.log(total=str(0), success=str(0), skipped=str(0), visited=str(0),
                 message='Loading known data')
        forums = Forum.objects.filter(stop=False).order_by("-activity")
        for forum in forums:
            if forum.id != home_forum_id:
                self.links.append([forum.domain, forum.verified_forum_id, 'old', forum.board_id])
            self.tracked.append(forum.domain)
            self.tracked.append(forum.board_id)

    def check_stop_signal(self):
        session = BotSession.objects.filter(session_id=self.session_id).first()
        if session.stop_signal:
            return True
        else:
            return False




    def work(self, url, id, home_forum_id, stop_list=False, templates=False, custom_login_code={}):
        print('Starting control at ' + datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        self.load_from_db(home_forum_id)
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

            link = self.get_topic_url(self.links[n][0]+'/viewforum.php?id='+str(self.links[n][1]))
            partner_domain = self.links[n][0]
            print(self.links[n][0]+'/viewforum.php?id='+str(self.links[n][1]) + ' - ' + str(link))
            if not link:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Could not find ad topic or load page: ' + self.links[n][0])
                continue

            try:
                self.driver2.get(link)
                assert self.driver2.current_url == link
            except:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Could not load page: ' + link)
                continue

            self.go_to_last_page(self.driver2)
            total = len(self.links)

            try:
                code_partner = self.get_code(self.driver2)
                if not self.validate_code(code_partner):
                    skipped += 1
                    self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                             message='Invalid code: ' + link)
                    continue
            except:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='No code: ' + link)
                continue

            if partner_domain in custom_login_code:
                logged_id = self.custom_login_code(self.driver2, link, custom_login_code[partner_domain])
            else:
                logged_id = self.login(self.driver2, link)

            if logged_id:
                form = self.check_answer_form(self.driver2)
                if form:
                    self.post(self.driver1, code_partner)
                    self_form = self.check_answer_form(self.driver1)
                    cur_link = self.find_current_link(self.driver1)

                    full_code_home = chosen_code + '\n' + '[url=' + cur_link + ']Ваша реклама[/url]'
                    self.post(self.driver2, full_code_home)
                    success += 1
                    self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                             message="Success: " + link)

                    if not self_form:
                        self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                                 message='Your topic is over!')
                        break
                else:
                    skipped += 1
                    self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                             message='No message form: ' + link)
                    continue
            else:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Not logged in: ' + link)
                continue
        if self.custom_l:
            self.log_out(self.driver1,  self.home_base)
        self.driver2.quit()
        self.driver1.quit()

        self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                 message="Finished!")
        return visited, success, self.links
