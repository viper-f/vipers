from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from asgiref.sync import async_to_sync
import json


class Advertiser:
    def __init__(self, log_mode='console', channel=None, group_name=None):
        self.driver1 = webdriver.Chrome()
        self.driver2 = webdriver.Chrome()
        self.links = []
        self.tracked = []
        self.log_mode = log_mode
        self.channel = channel
        self.group_name = group_name

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

    def scrape_links(self, driver):
        links = []
        posts = driver.find_elements(By.CLASS_NAME, "post-content")
        for post in posts:
            urls = post.find_elements(By.TAG_NAME, 'a')
            for url in urls:
                text = url.text
                if not text == '' and '#p' in text:
                    l = url.get_attribute('href')
                    track = l.split('/viewtopic')[0]
                    if track not in self.tracked:
                        parts = l.split('#')
                        self.links.append(parts[0])
                        self.tracked.append(track)

    def login(self, driver):
        try:
            driver.execute_script("return PR['in_1']();")
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )
            return True
        except:
            return False

    def get_code(self, driver):
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".topicpost"))
        )
        driver.execute_script("$('.topicpost .post-content .spoiler-box > blockquote').css('display', 'block');")
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".topicpost pre:first-child"))
        )
        return element.text

    def check_answer_form(self, driver):
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mail-reply, #post'))
            )
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
            form = driver.find_element(By.ID, "main-reply")
        except:
            return False
        form.clear()
        form.send_keys(message)
        driver.find_element(By.CSS_SELECTOR, '.punbb .formsubmit input.submit').click()
        return True

    def go_to_last_page(self, driver):
        if len(driver.find_elements(By.CSS_SELECTOR, '.linkst .pagelink a:nth-last-child(2)')) > 0:
            last_page = driver.find_element(By.CSS_SELECTOR, '.linkst .pagelink a:nth-last-child(2)').get_attribute(
                'href')
            driver.get(last_page)

    def find_last_post_link(self, driver):
        permalink = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.endpost .permalink'))
        )
        return permalink.get_attribute("href")

    def work(self, url):
        self.driver1.get(url)
        code_home = self.get_code(self.driver1)
        self.login(self.driver1)
        self.scrape_links(self.driver1)
        n = 0
        while n < len(self.links):
            self.driver2.get(self.links[n])
            self.scrape_links(self.driver2)
            code_partner = self.get_code(self.driver2)
            logged_id = self.login(self.driver2)
            if logged_id:
                form = self.check_answer_form(self.driver2)
                if form:
                    self.post(self.driver1, code_partner)
                    self.go_to_last_page(self.driver1)
                    self_form = self.check_answer_form(self.driver1)
                    link = self.find_last_post_link(self.driver1)
                    full_code_home = code_home + '\n' + '[url=' + link + ']Ваша реклама[/url]'
                    # self.post(self.driver2, full_code_home)
                    if not self_form:
                        self.log('Topic is over')
                        return
                else:
                    self.log('No message form:' + self.links[n])
            else:
                self.log('Not logged in:' + self.links[n])
            n += 1
            self.log('Visited: ' + str(n) + '; Total:' + str(len(self.links)))
