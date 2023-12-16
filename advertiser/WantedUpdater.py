from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class WantedUpdater:
    def __init__(self ):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.page_load_strategy = 'eager'

        try:
            self.driver = webdriver.Chrome(options=options)
        except NoSuchDriverException:
            exit(code=500)

    def parse_list(self, url):
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'html.parser')
        list = soup.css.select('blockquote')[1]
        text = list.decode_contents()
        text = text.replace('<span style="display: block; text-align: center"><span style="font-size: 14px">', '[align=center][size=14]')
        text = text.replace('<span style="font-style: italic">', '[i]')
        text = text.replace('</span>:</span></span></p><hr/>', '[/i]:[/size][/align]\n[hr]')
        text = text.replace('<p>', '')
        text = text.replace('</p>', "\n")
        text = text.replace('<span style="font-size: 18px"><span style="font-family: Georgia">', '[size=18][font=Georgia]')
        text = text.replace('</span></span>', '[/font][/size]')
        text = text.replace('<br/>', "\n")
        text = text.replace('<a href="', '[url=')
        text = text.replace('">', ']')
        text = text.replace('</a>', '[/url]')
        return text

    def custom_login(self, base_url, username, password):
        try:
            self.driver.get(base_url + '/login.php')
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#pun-main .formal>#login"))
            )
            form = self.driver.find_element(By.CSS_SELECTOR, "#pun-main .formal>#login")
            form.find_element(By.ID, "fld1").send_keys(username)
            form.find_element(By.ID, "fld2").send_keys(password)
            form.find_element(By.NAME, "login").click()
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )
            self.logged_in = True
            return True
        except:
            return False

    def post(self, driver, message):
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mail-reply'))
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

    def work(self, donor_url, receiver_url_base, receiver_post_id, login, password):
        print('Wanted updater: starting work at ' + datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        code = self.parse_list(donor_url)
        self.custom_login(receiver_url_base, login, password)
        self.driver.get(receiver_url_base + '/edit.php?id='+str(receiver_post_id)+'&action=edit')
        self.post(self.driver, code)
        sleep(2)
        self.driver.close()


