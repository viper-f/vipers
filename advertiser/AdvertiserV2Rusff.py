from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import sys

from advertiser.AdvertiserV2 import AdvertiserV2

sys.path.insert(0, './../vipers')
import vipers
import django
django.setup()


class AdvertiserV2Rusff (AdvertiserV2):

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



    def work(self, url, id, home_forum_id, stop_list=False, templates=False, custom_login_code={}):
        print('Starting work at ' + datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        self.load_forum_settings(id)
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

        total = 0
        success = 0
        skipped = 0
        visited = 0

        if not self.logged_in:
            self.login(self.driver1, url)
        self_form = self.check_answer_form(self.driver1)
        if not self_form:
            self.log(total=str(0), success=str(0), skipped=str(0), visited=str(0),
                     message='Your ad topic is over! Please, update forum settings!')
            return visited, success, self.links

        n = -1
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
                             message='Could not find ad topic or load page: ' + self.links[n][0])
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
                    self.go_to_last_page(self.driver1)
                    cur_link = self.find_last_post_link(self.driver1)

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
        if self.custom_l:
            self.log_out(self.driver1,  self.home_base)
        self.driver2.quit()
        self.driver1.quit()

        self.log(total=str(total), success=str(success), skipped=str(skipped), visited=str(visited),
                 message="Finished!")
        return visited, success, self.links
