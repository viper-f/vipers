from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class Advertiser:
    def __init__(self, log_mode='console', channel=None, group_name=None):
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        self.driver1 = webdriver.Chrome(options=options)
        self.driver2 = webdriver.Chrome(options=options)
        self.links = []
        self.tracked = []
        self.log_mode = log_mode
        self.channel = channel
        self.group_name = group_name
        self.home_base = ''
        self.logged_in = False

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
                if not text == '' and ('#p' in text or text.lower() == 'ваша реклама'):
                    l = url.get_attribute('href')
                    if "action=search" in l:
                        continue
                    track = l.split('/viewtopic')[0]
                    print(track + ' - ' + self.home_base)
                    if self.home_base in l:
                        self_present = True
                    if track not in self.tracked:
                        parts = l.split('#')
                        self.links.append(parts[0])
                        self.tracked.append(track)
        print(" -- ")
        return self_present

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

    def custom_login(self, url, username, password):
        try:
            self.driver1.get(url)
            button = self.driver1.find_element(By.ID, "navlogin")
            button.click()
            WebDriverWait(self.driver1, 5).until(
                EC.presence_of_element_located((By.ID, "form-login"))
            )
            self.driver1.find_element(By.ID, "fld1").send_keys(username)
            self.driver1.find_element(By.ID, "fld2").send_keys(password)
            self.driver1.find_element(By.NAME, "login").click()
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
            form = driver.find_element(By.ID, "main-reply")
        except:
            return False
        form.clear()
        form.send_keys(message)
        driver.find_element(By.CSS_SELECTOR, '.punbb .formsubmit input.submit').click()
        return True

    def go_to_last_page(self, driver):
        if len(driver.find_elements(By.CSS_SELECTOR, '.linkst .pagelink a.next')) > 0:
            next_page = driver.find_elements(By.CSS_SELECTOR, '.linkst .pagelink a.next')[0]
            last_page = next_page.find_element(By.XPATH, "preceding-sibling::*[1]").get_attribute(
                'href')
            driver.get(last_page)
            WebDriverWait(self.driver1, 5).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )

    def find_last_post_link(self, driver):
        permalink = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.endpost .permalink'))
        )
        return permalink.get_attribute("href")

    def find_current_link(self, driver):
        return driver.current_url

    def work(self, url, start_url=False, stop_list=False):
        track = url.split('/viewtopic')[0]
        self.tracked.append(track)
        if stop_list is not False:
            self.tracked += stop_list
        self.home_base = track

        if not start_url:
            start_url = url
        self.driver1.get(start_url)
        self.scrape_links(self.driver1)

        self.driver1.get(url)
        code_home = self.get_code(self.driver1)

        if not self.logged_in:
            self.login(self.driver1, url)
        n = 0
        total = 0
        success = 0
        skipped = 0
        visited = 0
        while n < len(self.links):
            self.driver2.get(self.links[n])
            self.go_to_last_page(self.driver2)
            self_present = self.scrape_links(self.driver2)
            total = len(self.links)

            if self_present:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Already has our post on the last page: ' + self.links[n])
                n += 1
                continue

            try:
                code_partner = self.get_code(self.driver2)
            except:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='No code:' + self.links[n])
                n += 1
                continue

            #   code_partner += "\n\n[size=10][Posted by bot][/size]"
            logged_id = self.login(self.driver2, self.links[n])
            if logged_id:
                form = self.check_answer_form(self.driver2)
                if form:
                    self.post(self.driver1, code_partner)
                    self_form = self.check_answer_form(self.driver1)
                    link = self.find_current_link(self.driver1)
                    full_code_home = code_home + '\n' + '[url=' + link + ']Ваша реклама[/url]'
                    self.post(self.driver2, full_code_home)
                    success += 1
                    if not self_form:
                        skipped += 1
                        self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                                 message='Topic is over')
                        return
                else:
                    skipped += 1
                    self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                             message='No message form:' + self.links[n])
                    n += 1
                    continue
            else:
                skipped += 1
                self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                         message='Not logged in:' + self.links[n])
                n += 1
                continue
            n += 1
            visited += 1
            self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                     message="continue")
