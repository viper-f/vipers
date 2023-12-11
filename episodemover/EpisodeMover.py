from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from urllib.parse import parse_qs
import re
from asgiref.sync import async_to_sync
import json
from datetime import datetime
import sys
import tensorflow as tf
from django.conf import settings


# sys.path.insert(0, './../vipers')
# import vipers
# import django
# django.setup()


class EpisodeMover:
    def __init__(self, log_mode='console', channel=None, session_id=None):
        self.log_mode = log_mode
        self.session_id = session_id
        self.channel = channel
        self.group_name = 'comm_' + session_id

    def initBrowser(self):
        options = Options()
       # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.page_load_strategy = 'eager'
        return webdriver.Chrome(options=options)

    def log(self, total, success, message):
        if self.log_mode == 'console':
            print('Total: ' + str(total) + '; Success: ' + str(success) + '; Message: ' + str(message))
        if self.log_mode == 'channel':
            async_to_sync(self.channel.group_send)(
                self.group_name,
                {
                    'type': 'log_message',
                    'message': json.dumps({
                        "total": total,
                        "visited": 0,
                        "success": success,
                        "skipped": 0,
                        "message": message
                    }),
                })

    def custom_login(self, driver, url, username, password):
        try:
            base_url = url.split('/viewtopic')[0]
            driver.get(base_url + '/login.php')
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#pun-main .formal>#login"))
            )
            form = driver.find_element(By.CSS_SELECTOR, "#pun-main .formal>#login")
            form.find_element(By.ID, "fld1").send_keys(username)
            form.find_element(By.ID, "fld2").send_keys(password)
            form.find_element(By.NAME, "login").click()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )
            return True
        except:
            return False

    def get_topic_map(self, driver, topic_url):
        base_url = topic_url.split('/viewtopic')[0]
        parsed_url = urlparse(topic_url)
        topic_id = parse_qs(parsed_url.query)['id'][0]
        driver.get(base_url + '/api.php?method=post.get&topic_id='+topic_id+'&sort_by=posted&sort_dir=asc&limit=100&skip=1&fields=id,username')
        text = driver.find_element(By.CSS_SELECTOR, "pre").text
        data = json.loads(text)
        usernames = []

        for post in data['response']:
            if post["username"] not in usernames:
                usernames.append(post['username'])
        return usernames, data['response']

    def post(self, driver, message):
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mail-reply, #post'))
            )
        except:
            driver.find_element(By.TAG_NAME, 'body').send_keys("Keys.ESCAPE")
        try:
            tarea = driver.find_element(By.ID, "main-reply")
        except:
            return False
        tarea.clear()
        driver.execute_script("arguments[0].value = arguments[1]", tarea, message)
        driver.execute_script("document.querySelector('.punbb .formsubmit input.submit').click()")
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.jGrowl-message a'))
            ).get_attribute('href')
        except:
            pass
        #tarea.send_keys(message)
        return True



    def work(self, old_episode, new_episode, characters):
        base_url_old = old_episode.split('/viewtopic')[0]
        browsers = {}
        provided_usernames = []
        mapping = {}
        for character in characters:
            browsers['old_'+character['old']['name']] = self.initBrowser()
            self.log(0, 0, 'Logging in as '+character['old']['name']+' on the old forum')
            status = self.custom_login(browsers['old_'+character['old']['name']], old_episode, character['old']['name'], character['old']['password'])
            if status:
                self.log(0, 0, 'Success')
            else:
                self.log(0, 0, 'Login failed. Aborting...')

            if character['old']['name'] not in provided_usernames:
                provided_usernames.append(character['old']['name'])

            browsers['new_'+character['new']['name']] = self.initBrowser()
            self.log(0, 0, 'Logging in as ' + character['new']['name'] + ' on the new forum')
            status = self.custom_login(browsers['new_'+character['new']['name']], new_episode, character['new']['name'], character['new']['password'])
            if status:
                self.log(0, 0, 'Success')
            else:
                self.log(0, 0, 'Login failed. Aborting...')
                return 0

            browsers['new_' + character['new']['name']].get(new_episode)
            mapping['old_'+character['old']['name']] = 'new_'+character['new']['name']

        required_usernames, old_posts = self.get_topic_map(browsers['old_'+characters[0]['old']['name']], old_episode)
        if len(set(required_usernames) - set(provided_usernames)):
            self.log(0, 0, 'Mismatch in usernames provided for old forum. Aborting...')
            return 0

        total = len(old_posts)
        success = 0
        for old_post in old_posts:
            browsers['old_'+old_post['username']].get(base_url_old + '/edit.php?id=' + str(old_post['id']) + '&action=edit')
            text = browsers['old_' + old_post['username']].find_element(By.ID, 'main-reply').text
            self.post(browsers[mapping['old_'+old_post['username']]], text)
            success += 1
            self.log(total, success, 'Post ' + str(old_post['id']) + ' from ' + old_post['username'] + ' was published')




m = EpisodeMover(channel="0", session_id="0")
m.work('https://kingscross.f-rpg.me/viewtopic.php?id=6750#p846032',
       'https://forum.viper-frpg.ovh/viewtopic.php?id=10#p250',
       [
           {
               "old": {
                   "name": "Assistant",
                   "password": "12345"
               },
               "new": {
                   "name": "PR",
                   "password": "1111"
               }
           },
{
               "old": {
                   "name": "Raphael",
                   "password": "mvpEsi5l"
               },
               "new": {
                   "name": "viper",
                   "password": "zyzVNtjc"
               }
           }
       ])
