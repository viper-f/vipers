from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
from asgiref.sync import async_to_sync
import json
from datetime import datetime
from topic_search import analize
import sys
import tensorflow as tf
import numpy as np

sys.path.insert(0, './../vipers')
import vipers
import django
django.setup()
from advertiser.models import Forum, BotSession, AdTemplate


class AdvertiserV2:
    def __init__(self, log_mode='console', channel=None, session_id=None):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.page_load_strategy = 'eager'
        self.driver1 = webdriver.Chrome(options=options)
        self.driver2 = webdriver.Chrome(options=options)
        self.links = []
        self.tracked = []
        self.log_mode = log_mode
        self.session_id = session_id
        self.channel = channel
        self.group_name = 'comm_' + session_id
        self.home_base = ''
        self.logged_in = False
        self.model = tf.keras.models.load_model('topic_model')
        self.templates = []


    def load_templates(self, ids):
        templates = AdTemplate.objects.filter(id__in=ids)
        template_dict = {}
        for template in templates:
            template_dict[template.id] = {
                'code': template.code,
                'sample': self.sample_template(template.code)
            }
        for tid in ids:
            self.templates.append(template_dict[tid])


    def get_topic_url(self, url):
        X, data = analize(url)
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


    def load_from_db(self, home_forum_id):
        self.log(total=str(0), success=str(0), skipped=str(0), visited=str(0),
                 message='Loading known data')
        forums = Forum.objects.filter(stop=False)
        for forum in forums:
            if forum.id != home_forum_id:
                self.links.append([forum.domain, forum.verified_forum_id, 'old'])
            self.tracked.append(forum.domain)

    def check_stop_signal(self):
        session = BotSession.objects.filter(session_id=self.session_id).first()
        if session.stop_signal:
            return True
        else:
            return False


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

    def test(self):
        self.driver1.get("https://www.selenium.dev/selenium/web/web-form.html")
        title = self.driver1.title
        return title

    def validate_code(self, code):
        counter = 0
        for i in range(0, len(code)):
            if code[i] == '[':
                counter += 1
            if code[i] == ']':
                counter -= 1
        if counter != 0:
            return False

        tags = ['/url', 'img', '/img', 'align=center', '/align']
        for tag in tags:
            pos = code.find(tag)
            if pos == -1:
                continue
            if code[pos - 1] != '[':
                return False
            if code[pos + len(tag)] != ']':
                return False
        return True

    def check_self_present(self, sample, driver):
        for img in sample:
            el = driver.find_elements(By.CSS_SELECTOR, 'img[src="'+img+'"]')
            if not len(el):
                return False
        return True

    def scrape_links(self, driver):
        posts = driver.find_elements(By.CLASS_NAME, "post-content")
        for post in posts:
            urls = post.find_elements(By.TAG_NAME, 'a')
            for url in urls:
                text = url.text
                if not text == '' and ('#p' in text or text.lower() == 'ваша реклама'):
                    l = url.get_attribute('href')
                    if "action=search" in l:
                        continue
                    l = l.replace("http://", "https://")
                    track = l.split('/viewtopic')[0]
                    if track not in self.tracked:
                        parts = l.split('#')
                        self.links.append([parts[0], 0, 'new'])
                        self.tracked.append(track)

    def login(self, driver, url):
        try:
            driver.execute_script("return PR['in_1']();")
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )
            self.logged_in = True
            return True
        except:
            try:
                driver.execute_script("PiarIn();")
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "navlogout"))
                )
                driver.get(url)
                self.logged_in = True
                return True
            except:
                return False

    def custom_login_code(self, driver, url, code):
        try:
            driver.execute_script(code)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )
            driver.get(url)
            self.logged_in = True
            return True
        except:
            return False

    def custom_login(self, url, username, password):
        try:
            base_url = url.split('/viewtopic')[0]
            self.driver1.get(base_url + '/login.php')
            WebDriverWait(self.driver1, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#pun-main .formal>#login"))
            )
            form = self.driver1.find_element(By.CSS_SELECTOR, "#pun-main .formal>#login")
            form.find_element(By.ID, "fld1").send_keys(username)
            form.find_element(By.ID, "fld2").send_keys(password)
            form.find_element(By.NAME, "login").click()
            WebDriverWait(self.driver1, 5).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )
            self.logged_in = True
            return True
        except:
            return False

    def get_code(self, driver):
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".topicpost"))
        )
        driver.execute_script("$('.topicpost .post-content .spoiler-box > blockquote').css('display', 'block');")
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".topicpost pre:first-child"))
        )
        return element.text

    def sample_template(self, code):
        return re.findall(r'\[img\]([^\[]*)\[\/img\]', code)

    def check_answer_form(self, driver):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mail-reply, #post'))
            )
            form = driver.find_element(By.ID, "main-reply")
            form.clear()
        except:
            return False
        return True

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
        #tarea.send_keys(message)
        driver.execute_script("document.querySelector('.punbb .formsubmit input.submit').click()")
        return True

    def go_to_last_page(self, driver):
        if len(driver.find_elements(By.CSS_SELECTOR, '.linkst .pagelink a.next')) > 0:
            next_page = driver.find_elements(By.CSS_SELECTOR, '.linkst .pagelink a.next')[0]
            last_page = next_page.find_element(By.XPATH, "preceding-sibling::*[1]").get_attribute(
                'href')
            driver.get(last_page)

    def find_last_post_link(self, driver):
        permalink = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.endpost .permalink'))
        )
        return permalink.get_attribute("href")

    def find_current_link(self, driver):
        return driver.current_url

    def work(self, url, home_forum_id, stop_list=False, templates=False, custom_login_code={}):
        print('Starting work at ' + datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        self.load_from_db(home_forum_id)
        self.log(total=str(0), success=str(0), skipped=str(0), visited=str(0),
                 message='Starting')
        track = url.split('/viewtopic')[0]
        self.tracked.append(track)
        if stop_list is not False:
            self.tracked += stop_list
        self.home_base = track

        self.driver1.get(url)
        if templates is False:
            home_code = self.get_code(self.driver1),
            self.templates.append({
                'code': home_code,
                'sample': self.sample_template(home_code)
            })
        else:
            self.load_templates(templates)

        if not self.logged_in:
            self.login(self.driver1, url)
        self_form = self.check_answer_form(self.driver1)
        if not self_form:
            self.log(total=str(0), success=str(0), skipped=str(0), visited=str(0),
                     message='Your ad topic is over! Please, update forum settings!')
        n = -1
        total = 0
        success = 0
        skipped = 0
        visited = 0
        #while n < 10:
        while n < len(self.links) - 1:

            if self.check_stop_signal():
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Stop signal received')
                break

            n += 1
            visited += 1
            link = self.links[n][0]

            if self.links[n][2] == 'old':
                link = self.get_topic_url(self.links[n][0]+'/viewforum.php?id='+str(self.links[n][1]))
                partner_domain = self.links[n][0]
                print(self.links[n][0]+'/viewforum.php?id='+str(self.links[n][1]) + ' - ' + str(link))
                if not link:
                    skipped += 1
                    self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                             message='Could not find ad topic: ' + self.links[n][0])
                    continue

            try:
                self.driver2.get(link)
                assert self.driver2.current_url == link
            except:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Could not load page: ' + link)
                continue

            if self.links[n][2] == 'new':
                partner_domain = link.split('/viewtopic')[0]
                try:
                    self.links[n][0] = partner_domain
                    self.links[n][1] = self.driver2.execute_script('return FORUM.topic.forum_id')
                except:
                    print("Could not grab forum id: " + link)

            self.go_to_last_page(self.driver2)
            self.scrape_links(self.driver2)
            total = len(self.links)

            chosen_code = False
            for template in self.templates:
                self_present = self.check_self_present(template['sample'], self.driver2)
                if not self_present:
                    chosen_code = template['code']
                    break

            if not chosen_code:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='All posts present on last page: ' + link)
                continue

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
        self.driver2.quit()
        self.driver1.quit()

        self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                 message="Finished!")
        return visited, success, self.links
