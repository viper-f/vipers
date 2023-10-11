from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.home_base = ''

    def log(self, total, success, skipped, visited, message):
        if self.log_mode == 'console':
            print('Total: ' + total + '; Success: ' + success + '; Message: ' + message)

    def test(self):
        self.driver1.get("https://www.selenium.dev/selenium/web/web-form.html")
        title = self.driver1.title
        return title

    def scrape_links(self, driver):
        self_present = False
        posts = driver.find_elements(By.CLASS_NAME, "post-content")
        for post in posts:
            urls = post.find_elements(By.TAG_NAME, 'a')
            for url in urls:
                text = url.text
                if not text == '' and '#p' in text:
                    l = url.get_attribute('href')
                    track = l.split('/viewtopic')[0]
                    print(track + ' - ' + self.home_base)
                    if track == self.home_base:
                        self_present = True
                    if track not in self.tracked:
                        parts = l.split('#')
                        self.links.append(parts[0])
                        self.tracked.append(track)
        return self_present

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

    def find_current_link(self, driver):
        return driver.current_url

    def check_post_already_preset(self, driver, url):
        if len(driver.find_elements(By.CSS_SELECTOR, '.linkst .pagelink a:nth-last-child(2)')) > 0:
            last_page = driver.find_element(By.CSS_SELECTOR, '.linkst .pagelink a:nth-last-child(2)').get_attribute(
                'href')

    def work(self, url):
        track = url.split('/viewtopic')[0]
        self.tracked.append(track)
        self.home_base = track

        self.driver1.get(url)
        code_home = self.get_code(self.driver1)
        self.login(self.driver1)
        self.scrape_links(self.driver1)
        n = 0
        total = 0
        success = 0
        skipped = 0
        visited = 0
        while n < len(self.links):
            self.driver2.get(self.links[n])
            self.go_to_last_page(self.driver2)
            self_present = self.scrape_links(self.driver2)

            if self_present:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Already has our post on the last page:' + self.links[n])
                continue

            total = len(self.links)
            try:
                code_partner = self.get_code(self.driver2)
            except:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='No code:' + self.links[n])
                continue

            code_partner += "\n\n[size=10][Posted by bot][/size]"
            logged_id = self.login(self.driver2)
            if logged_id:
                form = self.check_answer_form(self.driver2)
                if form:
                   # self.post(self.driver1, code_partner)
                    self_form = self.check_answer_form(self.driver1)
                    link = self.find_current_link(self.driver1)
                    full_code_home = code_home + '\n' + '[url=' + link + ']Ваша реклама[/url]'
                 # self.post(self.driver2, full_code_home)
                    success += 1
                    if not self_form:
                        skipped += 1
                        self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited), message='Topic is over')
                        return
                else:
                    skipped += 1
                    self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited), message='No message form:' + self.links[n])
            else:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited), message='Not logged in:' + self.links[n])
            n += 1
            visited += 1
            self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited), message="continue")
