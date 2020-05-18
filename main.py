import random
import string
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import errors
import logging
import time
import re
import os

YANDEX_PAGE_NUMBER = 1-1
EPICGAMES_PAGE_NUMBER = 2-1
TIMEOUT = 2000
REFRESH_SEC = 5

logging.basicConfig(filename="farm.log", level=logging.INFO, filemode='a')

# yandex captcha without js be more easy
# chrome_options = Options()
# chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})
# chrome = webdriver.Chrome('chromedriver',chrome_options=chrome_options)

class BaseDataClass():
    def __init__(self):
        self.webdriver = Chrome()
        self.firstname = ''.join(random.choice(string.ascii_lowercase) for i in range(9))
        self.lastname = ''.join(random.choice(string.ascii_lowercase) for i in range(9))
        self.login = f'{self.firstname}firstrev{self.lastname}'
        self.pswd = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(18))
        self.epicgames_login = self.login[:15]
    def get_all_atributes(self):
        for i in self.__dict__:
            logging.info(f'{i} - {getattr(self, i)}')
        logging.info('-'*100)
    def open_new_tab(self):
        self.webdriver.get('https://ya.ru/')
        self.webdriver.execute_script("window.open()")


class Yandex():
    def __init__(self, cls):
        self.__dict__ = cls.__dict__
        self.page_number = YANDEX_PAGE_NUMBER-1
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
        webdriver.find_element_by_xpath('//*[@id="hint_answer"]').send_keys('da')


    def press_submit_button(self, webdriver):
        # solve the captcha
        try:
            wait_for_element = WebDriverWait(webdriver, TIMEOUT).until_not(
                EC.url_contains('passport.yandex.ru/registration/mail'))
        except selenium.common.exceptions.TimeoutException:
            raise errors.CaptchaFailedException('solve the captcha yandex.ru')

    def take_code_from_msg(self, webdriver):
        self.true_code = None
        self.codes = []
        webdriver.get('https://mail.yandex.ru/lite')
        while True:
            elements = webdriver.find_elements_by_class_name('b-messages__message__left')
            for i in range(len(elements)):
                if re.findall('Epic Games', elements[i].text):
                    element = elements[i]
                    if element in self.codes:
                        pass
                    else:
                        self.true_code = re.findall('(\d{6})', element.text)[0]
                        self.codes.append(self.true_code)
                        break
                else:
                    webdriver.refresh()
                    time.sleep(REFRESH_SEC)
            if len(elements) == 0:
                webdriver.refresh()
                time.sleep(REFRESH_SEC)
            elif self.true_code != None:
                break
        code = self.true_code
        self.true_code = None
        return code


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
        webdriver.find_element_by_xpath('//*[@id="password"]').send_keys(self.pswd)
        webdriver.find_element_by_xpath('//*[@id="termsOfService"]').click()

    def press_submit_button(self, webdriver):
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-submit"]')))
        webdriver.find_element_by_xpath('//*[@id="btn-submit"]').click()

    def code_1(self, webdriver, code: str):
        webdriver.find_element_by_xpath('//*[@id="code"]').send_keys(code)
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="continue"]/span')))
        webdriver.find_element_by_xpath('//*[@id="continue"]/span').click()

    def code_2fa_open(self, webdriver):
        webdriver.get('https://www.epicgames.com/account/password#2fa-signup')
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(
            EC.element_to_be_clickable((
                By.CLASS_NAME, 'btn btn-custom btn-submit-custom email-auth')))
        webdriver.find_element_by_class_name(
            'btn btn-custom btn-submit-custom email-auth').click()

    def code_2fa_recieve(self, webdriver, code: str):
        webdriver.find_element_by_xpath(
            '//*[@id="emailChallengeModal"]/div[2]/div/div[3]/div/div/div/input').click()
        webdriver.find_element_by_xpath(
            '//*[@id="emailChallengeModal"]/div[2]/div/div[3]/div/div/div/input').send_keys(code)
        webdriver.find_element_by_xpath('//*[@id="emailChallengeModal"]/div[2]/div/div[4]/div[2]/button').click()



class Farmer():
    def run(self):
        # a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
        # a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
        a = BaseDataClass()
        self.dict = a.__dict__
        a.open_new_tab()
        a.get_all_atributes()
        yandex = Yandex(a)
        epicgames = Epicgamesstore(a)
        a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
        yandex.register(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
        epicgames.register(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
        yandex.press_submit_button(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
        epicgames.press_submit_button(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
        first_code = yandex.take_code_from_msg(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
        epicgames.code_1(a.webdriver, first_code)
        time.sleep(2)
        epicgames.code_2fa_open(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
        second_code = yandex.take_code_from_msg(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
        epicgames.code_2fa_recieve(a.webdriver, second_code)

    def run_threaded(self, workers = 1):
        for i in range(workers):
            self.run()



if __name__ == '__main__':
    farm = Farmer()
    farm.run()