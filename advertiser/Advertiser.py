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
            last_page = driver.find_element(By.CSS_SELECTOR, '.linkst .pagelink a:nth-last-child(2)').get_attribute('href')
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
        self.links += self.scrape_links(self.driver1, url)
        n = 0
        print(self.links)
        while n < len(self.links):
            self.driver2.get(self.links[n])
            code_partner = self.get_code(self.driver2)
            logged_id = self.login(self.driver2)
            if logged_id:
                self.post(self.driver1, code_partner)
                self.go_to_last_page(self.driver1)
                link = self.find_last_post_link(self.driver1)
                full_code_home = code_home + '\n' + '[url=' + link + ']Ваша реклама[/url]'
                #print(full_code_home)
                #self.post(self.driver2, full_code_home)
            else:
                print('Not logged in:' + self.links[n])
            n += 1



advertiser = Advertiser()
advertiser.work("http://viperstest.rusff.me/viewtopic.php?id=2#p2")
