import logging
import random
import re
import string
import threading
import time
import selenium
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import errors

YANDEX_PAGE_NUMBER = 1-1
EPICGAMES_PAGE_NUMBER = 2-1
TIMEOUT = 4000
REFRESH_SEC = 5

logging.basicConfig(filename="farm.log", level=logging.INFO, filemode='a')

chrome_options = webdriver.ChromeOptions()
# PROXY = '82.200.233.4:3128'
# chrome_options.add_argument('--proxy-server=%s' % PROXY)
# chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})


class BaseDataClass():
    def __init__(self):
        self.status = 'Init'
        self.webdriver = Chrome(chrome_options=chrome_options)
        self.firstname = ''.join(random.choice(string.ascii_lowercase) for i in range(7))
        self.lastname = ''.join(random.choice(string.ascii_lowercase) for i in range(7))
        self.login = f'{self.firstname}A{self.lastname}'
        self.pswd = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(18))
        self.epicgames_login = self.login[:15]
        self.epicgames_pswd = self.pswd
    def save_to_log_file(self):
        print(self.status)
        for i in self.__dict__:
            logging.info(f' {i} - {getattr(self, i)}')
        logging.info(' ' + '-'*100)
    def open_new_tab(self):
        self.webdriver.get('chrome://settings')
        self.webdriver.execute_script("window.open()")
    def close_webdriver(self):
        self.webdriver.close()


class Yandex():
    def __init__(self, cls):
        self.__dict__ = cls.__dict__
        self.page_number = YANDEX_PAGE_NUMBER-1

    def _js_disble_chromium(self, webdriver):
        webdriver.get('Chrome://settings/content/javascript')
        webdriver.find_element_by_tag_name('body').send_keys(
            Keys.TAB*6 + Keys.RETURN + 'passport.yandex.ru' + Keys.RETURN)

    def _js_switcher(self, webdriver):
        webdriver.get('Chrome://settings/content/javascript')
        webdriver.find_element_by_tag_name('body').send_keys(Keys.TAB*5 + Keys.RETURN)

    def register(self, webdriver):
        webdriver.get('https://passport.yandex.ru/registration/mail')
        # may include verification of a phone number or email
        try:
            wait_for_page_load = WebDriverWait(webdriver, 4).until(EC.url_contains("registration/mail"))
        except selenium.common.exceptions.TimeoutException:
            raise errors.BadIpRequestException('Try to change proxy or wait')

        webdriver.find_element_by_xpath('//*[@id="firstname"]').send_keys(self.firstname)
        webdriver.find_element_by_xpath('//*[@id="lastname"]').send_keys(self.lastname)
        webdriver.find_element_by_xpath('//*[@id="login"]').send_keys(self.login)
        webdriver.find_element_by_xpath('//*[@id="password"]').send_keys(self.pswd)
        webdriver.find_element_by_xpath('//*[@id="password_confirm"]').send_keys(self.pswd)
        webdriver.find_element_by_xpath(
            '//*[@id="root"]/div/div[2]/div/main/div/div/div/form/div[3]/div/div[2]/div/span').click()
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(EC.element_to_be_clickable((
            By.XPATH, '//*[@id="hint_answer"]')))
        webdriver.find_element_by_xpath('//*[@id="hint_answer"]').send_keys('da')


    def press_submit_button(self, webdriver):
        # solve the captcha
        try:
            wait_for_element = WebDriverWait(webdriver, TIMEOUT).until_not(
                EC.url_contains('passport.yandex.ru/registration/mail'))
        except selenium.common.exceptions.TimeoutException:
            raise errors.CaptchaFailedException('solve the captcha yandex.ru')
        self.status = 'Yandex account registered'

    def take_first_code(self, webdriver):
        self.first_code = None
        webdriver.get('https://mail.yandex.ru/lite')
        while self.first_code == None:
            elements = webdriver.find_elements_by_class_name('b-messages__message__left')
            for i in range(len(elements)):
                try:
                    element = elements[i].text
                    if len(re.findall('! (\d{6})', element)) != 0:
                        self.first_code = re.findall('! (\d{6})', element)[0]
                except:
                    pass
                else:
                    time.sleep(REFRESH_SEC)
                    webdriver.refresh()
            time.sleep(REFRESH_SEC)
            webdriver.refresh()
        print(self.first_code)
        return self.first_code

    def take_second_code(self, webdriver):
        self.second_code = None
        webdriver.get('https://mail.yandex.ru/lite')
        while self.second_code == None:
            elements = webdriver.find_elements_by_class_name('b-messages__message__left')
            for i in range(len(elements)):
                time.sleep(2)
                try:
                    element = elements[i].text
                    if len(re.findall(': (\d{6})', element)) != 0:
                        self.second_code = re.findall(': (\d{6})', element)[0]
                except:
                    pass
                else:
                    time.sleep(REFRESH_SEC)
                    webdriver.refresh()
            time.sleep(REFRESH_SEC)
            webdriver.refresh()
        print(self.second_code)
        return self.second_code

    def auth_with_data(self, webdriver, login, pswd):
        self.login = login
        self.pswd = pswd
        webdriver.get('https://passport.yandex.ru/auth')
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="passp-field-login"]')))
        webdriver.find_element_by_xpath('//*[@id="passp-field-login"]').send_keys(self.login + Keys.RETURN)
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.NAME, 'passwd')))
        webdriver.find_element_by_name('passwd').send_keys(self.pswd + Keys.RETURN)

    def link_to_reset_pswd(self, webdriver):
        self.restore_link = None
        webdriver.get('https://mail.yandex.ru/lite')
        while self.restore_link == None:
            elements = webdriver.find_elements_by_class_name('b-messages__message__left')
            for i in range(len(elements)):
                time.sleep(2)
                try:
                    element = elements[i].text
                    if len(re.findall('https://accounts.epicgames.com/resetPassword\?code=(\w{32})', element)) != 0:
                        self.restore_link = \
                        re.findall('https://accounts.epicgames.com/resetPassword\?code=(\w{32})', element)[0]
                except:
                    pass
                else:
                    time.sleep(REFRESH_SEC)
                    webdriver.refresh()
            time.sleep(REFRESH_SEC)
            webdriver.refresh()
        print(self.restore_link)
        return 'https://accounts.epicgames.com/resetPassword\?code=' + self.restore_link


class Epicgamesstore():
    def __init__(self, cls):
        self.__dict__ = cls.__dict__
        self.page_number = EPICGAMES_PAGE_NUMBER-1
    def register(self, webdriver, yandexmaildns='yandex.ru'):
        webdriver.get('https://www.epicgames.com/id/register')
        try:
            wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, 'name')))
        except selenium.common.exceptions.TimeoutException:
            raise errors.CaptchaFailedException('solve the captcha epicgames')

        webdriver.find_element_by_xpath('//*[@id="name"]').send_keys(self.firstname)
        webdriver.find_element_by_xpath('//*[@id="lastName"]').send_keys(self.lastname)
        webdriver.find_element_by_xpath('//*[@id="displayName"]').send_keys(self.epicgames_login)
        webdriver.find_element_by_xpath('//*[@id="email"]').send_keys(f'{self.login}@{yandexmaildns}')
        webdriver.find_element_by_xpath('//*[@id="password"]').send_keys(self.epicgames_pswd)
        webdriver.find_element_by_xpath('//*[@id="termsOfService"]').click()

    def press_submit_button(self, webdriver):
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-submit"]')))
        webdriver.find_element_by_xpath('//*[@id="btn-submit"]').click()

    def code_1(self, webdriver, code: str):
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="code"]')))
        webdriver.find_element_by_xpath('//*[@id="code"]').send_keys(code)
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="continue"]/span')))
        webdriver.find_element_by_xpath('//*[@id="continue"]/span').click()
        self.status = 'Epicgames account registered'

    def code_2fa_open(self, webdriver):
        webdriver.get('https://www.epicgames.com/account/password')
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn-custom btn-submit-custom email-auth')))
        buttons = webdriver.find_elements_by_class_name('btn-custom btn-submit-custom email-auth')
        for i in buttons:
            if re.findall('((E|e)mail)|((П|п)очте)',i.text):
                i.click()
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(EC.element_to_be_clickable((
            By.CLASS_NAME, 'input challengeEmailCode')))

    def code_2fa_recieve(self, webdriver, code: str):
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'input challengeEmailCode')))
        webdriver.find_element_by_class_name('input challengeEmailCode').click()
        webdriver.find_element_by_class_name('input challengeEmailCode').send_keys(code + Keys.RETURN)
        self.status = 'Epicgames 2fa activated'

    def get_gta_V(self, webdriver):
        # webdriver.get('https://www.epicgames.com/store/ru/product/grand-theft-auto-v/home')
        # webdriver.find_element_by_xpath('//*[@id="dieselReactWrapper"]/div/div[4]/main/div[2]/div/div[2]/div/button').click()
        # webdriver.find_element_by_xpath(
        #     '//*[@id="dieselReactWrapper"]/div/div[4]/main/div/div/div[2]/div/div[2]/div[2]/div/div/div[3]/div/div/div/div[3]/div/button').click()
        # webdriver.find_element_by_xpath()
        webdriver.get('https://launcher-website-prod07.ol.epicgames.com/purchase?showNavigation=true&namespace=0584d2013f0149a791e7b9bad0eec102&offers=954871df36d3456ca1face43aa5c2e62#/purchase/verify?_k=sx9l8u')
        self.status = 'Gta5 getted'

    def auth_with_data(self, webdriver, epicgames_login, epicgames_pswd):
        webdriver.get('https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fstore%2Fru%2F&noHostRedirect=true')
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, 'usernameOrEmail')))
        webdriver.find_element_by_id('usernameOrEmail').click()
        webdriver.find_element_by_id('usernameOrEmail').send_keys(epicgames_login)
        webdriver.find_element_by_id('password').send_keys(epicgames_pswd)
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, 'login')))
        webdriver.find_element_by_id('login').send_keys(Keys.RETURN)
        time.sleep(30)
        if re.findall('(\w+)-(\w+)-(\w+)', webdriver.find_element_by_tag_name('body').text):
            return 'need_reset'
        return 'ok'

    def request_to_reset_pswd(self, webdriver):
        webdriver.get('https://www.epicgames.com/id/login/forgot-password')
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, 'email')))
        print(wait_for_element)
        webdriver.find_element_by_id('email').click()
        # YANDEXDNS CHANGE IN FUTURE
        webdriver.find_element_by_id('email').send_keys(self.epicgames_login + '@yandex.ru')
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, 'send')))
        webdriver.find_element_by_id('send').send_keys(Keys.RETURN)

    def reset_pswd(self, webdriver, link, new_epicgames_pswd=None):
        if new_epicgames_pswd == None:
            self.new_epicgames_pswd == self.epicgames_pswd + '1'
        else:
            self.new_epicgames_pswd == new_epicgames_pswd
        webdriver.get(link)
        # self.status = 'epicgames_pswd_reseted'



class Farmer():
    # TODO compare run and run with data methods
    # TODO remove a.webdriver?
    workers_list = []
    def _run_without_data(self):
        try:
            a = BaseDataClass()
            self.dict = a.__dict__
            a.open_new_tab()
            yandex = Yandex(a)
            epicgames = Epicgamesstore(a)
            a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
            # here be disable js
            yandex.register(a.webdriver)
            a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
            # here be enable js
            epicgames.register(a.webdriver)
            time.sleep(2)
            a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
            yandex.press_submit_button(a.webdriver)
            a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
            epicgames.press_submit_button(a.webdriver)
            a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
            first_code = yandex.take_first_code(a.webdriver)
            a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
            epicgames.code_1(a.webdriver, first_code)
            epicgames.code_2fa_open(a.webdriver)
            a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
            second_code = yandex.take_second_code(a.webdriver)
            a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
            epicgames.code_2fa_recieve(a.webdriver, second_code)
            epicgames.get_gta_V(a.webdriver)
        finally:
            if a.status != 'Init':
                a.save_to_log_file()
            else:
                pass
            # a.close_webdriver()
    def _run_with_data(self, login, pswd, epicgames_login = None, epicgames_pswd = None):
        try:
            a = BaseDataClass()
            self.dict = a.__dict__
            a.open_new_tab()
            yandex = Yandex(a)
            epicgames = Epicgamesstore(a)
            a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
            # here be disable js
            yandex.auth_with_data(a.webdriver, login, pswd)
            a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
            # here be enable js
            if epicgames_login == None:
                epicgames.register(a.webdriver)
                time.sleep(2)
                a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
                yandex.press_submit_button(a.webdriver)
                a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
                epicgames.press_submit_button(a.webdriver)
                a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
                first_code = yandex.take_first_code(a.webdriver)
                a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
                epicgames.code_1(a.webdriver, first_code)
            else:
                status_code = epicgames.auth_with_data(a.webdriver, epicgames_login, pswd)
                a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
                if status_code == 'need_reset':
                    epicgames.request_to_reset_pswd(a.webdriver)
                a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
                if status_code == 'need_reset':
                    link = yandex.link_to_reset_pswd(a.webdriver)
                a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
                if status_code == 'need_reset':
                    epicgames.reset_pswd(a.webdriver, link)


            epicgames.code_2fa_open(a.webdriver)
            a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
            second_code = yandex.take_second_code(a.webdriver)
            a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
            epicgames.code_2fa_recieve(a.webdriver, second_code)
            epicgames.get_gta_V(a.webdriver)
        finally:
            if a.status != 'Init':
                a.save_to_log_file()
            else:
                pass
            # a.close_webdriver()

    def run(self, login = None, pswd = None, epicgames_login = None, epicgames_pswd = None):
        if login == None and pswd == None:
            self._run_without_data()
        else:
            self._run_with_data(login, pswd, epicgames_login, epicgames_pswd)

    def run_threaded(self, workers = 1, *args):
        for i in range(workers):
            self.add_worker(*args)

    def add_worker(self, args):
        thread = threading.Thread(target=self.run())
        self.workers_list.append(thread)
        thread.start()

    def check_workers(self):
        for i in self.workers_list:
            print(i)



if __name__ == '__main__':
    farm = Farmer()
    farm.run()