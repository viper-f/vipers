import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Advertiser:
    def __init__(self):
        self.driver1 = webdriver.Chrome()
        self.driver2 = webdriver.Chrome()
        self.links = []
        self.visited = []

    def test(self):
        self.driver1.get("https://www.selenium.dev/selenium/web/web-form.html")
        title = self.driver1.title
        return title

    def scrape_links(self, driver, page_url):
        links = []
        driver.get(page_url)
        posts = driver.find_elements(By.CLASS_NAME, "post-content")
        for post in posts:
            urls = post.find_elements(By.TAG_NAME, 'a')
            for url in urls:
                text = url.text
                if not text == '' and '#p' in text:
                    l = url.get_attribute('href')
                    parts = l.split('#')
                    links.append(parts[0])
        return links

    def login(self, driver):
        driver.execute_script("return PR['in_1']();")
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "navlogout"))
            )
        except:
            driver.quit()

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
            driver.find_element_by_tag_name('body').send_keys("Keys.ESCAPE")
        try:
            form = driver.find_element(By.ID, "main-reply")
        except:
            try:
                form = driver.find_element(By.ID, "post")
            except:
                return False
        form.clear()
        form.send_keys("Keys.CONTROL" + "a")
        form.send_keys("Keys.DELETE")
        form.send_keys(message)
        return True

    def work(self, url):
        self.driver1.get(url)
        code_home = self.get_code(self.driver1)
        print(code_home)
        self.login(self.driver1)
        self.links += self.scrape_links(self.driver1, url)
        n = 0
        # while n < len(self.links):
        #     self.driver2.get(self.links[n])
        #     code_partner = self.get_code(self.driver2)
        #     print(code_partner)
        #     n += 1



advertiser = Advertiser()
advertiser.work("https://kingscross.f-rpg.me/viewtopic.php?id=6471&p=42#p788489")
