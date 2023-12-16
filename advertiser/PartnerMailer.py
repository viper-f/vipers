from selenium import webdriver
from selenium.common import NoSuchDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import re
import csv
from asgiref.sync import async_to_sync
import json
from datetime import datetime



class PartnerMailer:
    def __init__(self, log_mode='console', channel=None, group_name=None):

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument("user-data-dir=/home/root/vipers/profile")

        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {
            "profile.managed_default_content_settings.images": 2,
                 }
        options.add_experimental_option("prefs", prefs)

        self.links = []
        self.tracked = []
        self.log_mode = log_mode
        self.channel = channel
        self.group_name = group_name
        self.home_base = ''
        self.logged_in = False

        try:
            self.driver2 = webdriver.Chrome(options=options)
        except NoSuchDriverException:
            exit(code=500)

    def check_cache_login(self, driver):
        try:
            driver.find_element(By.ID, "navlogout")
        except NoSuchElementException:
            return True
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

    def login(self, driver, url):
        if self.check_cache_login(driver):
            self.logged_in = True
            return True
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
        if self.check_cache_login(driver):
            self.logged_in = True
            return True
        try:
            driver.execute_script(code)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )
            driver.get(url)
            self.logged_in = True
            return True
        except:
            return False


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
        driver.execute_script("document.querySelector('.punbb .formsubmit input.submit').click()")
        return True

    def go_to_last_page(self, driver):
        if len(driver.find_elements(By.CSS_SELECTOR, '.linkst .pagelink a.next')) > 0:
            next_page = driver.find_elements(By.CSS_SELECTOR, '.linkst .pagelink a.next')[0]
            last_page = next_page.find_element(By.XPATH, "preceding-sibling::*[1]").get_attribute(
                'href')
            driver.get(last_page)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )

    def find_last_post_link(self, driver):
        permalink = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.endpost .permalink'))
        )
        return permalink.get_attribute("href")

    def work(self, urls, template, custom_login_code={}):
        print('Partner mailer: starting work at ' + datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        self.log(total=str(0), success=str(0), skipped=str(0), visited=str(0),
                 message='Starting')

        total = len(urls)
        success = 0
        skipped = 0
        visited = 0
        for url in urls:
            visited += 1
            try:
                self.driver2.get(url)
            except:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Could not load page: ' + url)
                continue
            partner_domain = url.split('/viewtopic')[0]

           # self.go_to_last_page(self.driver2)
            print(partner_domain)

            if partner_domain in custom_login_code:
                logged_id = self.custom_login_code(self.driver2, url, custom_login_code[partner_domain])
            else:
                logged_id = self.login(self.driver2, url)

            if logged_id:
                form = self.check_answer_form(self.driver2)
                if form:
                    self.post(self.driver2, template)
                    success += 1
                    self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                             message="Success: " + url)

                else:
                    skipped += 1
                    self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                             message='No message form: ' + url)
                    continue
            else:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Not logged in: ' + url)
                continue
        self.driver2.quit()

        self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                 message="Finished!")
        return visited, success
