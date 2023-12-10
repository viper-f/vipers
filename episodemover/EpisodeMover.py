from selenium import webdriver
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
from django.conf import settings


sys.path.insert(0, './../vipers')
import vipers
import django
django.setup()


class AdvertiserRusff:
    def __init__(self, log_mode='console', channel=None, session_id=None):
        self.log_mode = log_mode
        self.session_id = session_id
        self.channel = channel
        self.group_name = 'comm_' + session_id

    def initBrowser(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.page_load_strategy = 'eager'
        return webdriver.Chrome(options=options)

    def log(self, total, success, message):
        if self.log_mode == 'console':
            print('Total: ' + total + '; Success: ' + success + '; Message: ' + message)
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
            driver.get(url)
            return True
        except:
            return False

    def work(self, old_episode, new_episode, characters):
        browsers = {}
        for character in characters:
            browsers[character['old']['name']] = self.initBrowser()
            self.log(0, 0, 'Logging in as '+character['old']['name']+' on the old forum')
            status = self.custom_login(browsers[character['old']['name']], old_episode, character['old']['name'], character['old']['password'])
            if status:
                self.log(0, 0, 'Success')
            else:
                self.log(0, 0, 'Login failed. Aborting...')
            browsers[character['new']['name']] = self.initBrowser()
            self.log(0, 0, 'Logging in as ' + character['new']['name'] + ' on the new forum')
            status = self.custom_login(browsers[character['new']['name']], new_episode, character['new']['name'], character['new']['password'])
            if status:
                self.log(0, 0, 'Success')
            else:
                self.log(0, 0, 'Login failed. Aborting...')



