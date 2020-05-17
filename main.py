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
import os

YANDEX_PAGE_NUMBER = 1-1
EPICGAMES_PAGE_NUMBER = 2-1
TIMEOUT = 2000

logging.basicConfig(filename="farm.log", level=logging.INFO, filemode='a')

# yandex captcha without js be more easy
# chrome_options = Options()
# chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})
# chrome = webdriver.Chrome('chromedriver',chrome_options=chrome_options)

class BaseDataClass():
    def __init__(self):
        self.webdriver = Chrome(l)
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
            wait_for_page_load = WebDriverWait(webdriver, 4
                                               ).until(EC.url_contains("registration/mail"))
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
        # solve the captcha
        try:
            wait_for_element = WebDriverWait(webdriver, TIMEOUT).until_not(EC.url_contains('passport.yandex.ru/registration/mail'))
        except selenium.common.exceptions.TimeoutException:
            raise errors.CaptchaFailedException('solve the captcha yandex.ru')

    def open_last_msg(self, webdriver):
        webdriver.get('https://mail.yandex.ru/lite')
        while True:
            element = webdriver.find_elements_by_xpath('//*[@id="main"]/div/div[1]')
            if  element == None:
                break
            else:
                print(element)
                webdriver.refresh()
                time.sleep(3)
        first_message = element
        print(first_message)

    def _take_first_code(self, webdriver):
        webdriver.find_element_by_xpath(
            '//*[@id="nb-1"]/body/div[9]/div/div/div/div/div/div/div/div[2]/div[4]/button[1]').click()
        code = webdriver.find_element_by_xpath(
            '//*[@id="nb-1"]/body/div[2]/div[5]/div/div[3]/div[3]/div[2]/div[5]/div[1]/div/div[3]/div/div/table/tbody/tr/td/center/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td/div')
        code = code.get_attribute()
        print(code)
    def _take_2fa_code(self, webdriver):
        pass


class Epicgamesstore():
    def __init__(self, cls):
        self.__dict__ = cls.__dict__
        self.page_number = EPICGAMES_PAGE_NUMBER-1
    def register(self, webdriver, yandexmaildns='yandex.ru'):
        webdriver.get('https://www.epicgames.com/id/register')
        try:
            wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(EC.visibility_of_element_located((By.ID, 'name')))
        except selenium.common.exceptions.TimeoutException:
            raise errors.CaptchaFailedException('solve the captcha epicgames')

        webdriver.find_element_by_xpath('//*[@id="name"]').send_keys(self.firstname)
        webdriver.find_element_by_xpath('//*[@id="lastName"]').send_keys(self.lastname)
        webdriver.find_element_by_xpath('//*[@id="displayName"]').send_keys(self.epicgames_login)
        webdriver.find_element_by_xpath('//*[@id="email"]').send_keys(f'{self.login}@{yandexmaildns}')
        webdriver.find_element_by_xpath('//*[@id="password"]').send_keys(self.pswd)
        webdriver.find_element_by_xpath('//*[@id="termsOfService"]').click()
        wait_for_element = WebDriverWait(webdriver, TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-submit"]')))
        webdriver.find_element_by_xpath('//*[@id="btn-submit"]').click()

    def open_first_window(self, webdriver):
        webdriver.get('https://www.epicgames.com/id/register')

class Farmer():
    def run(self):
        a = BaseDataClass()
        self.dict = a.__dict__
        a.open_new_tab()
        a.get_all_atributes()
        yandex = Yandex(a)
        epicgames = Epicgamesstore(a)
        a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
        epicgames.open_first_window(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
        yandex.register(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[EPICGAMES_PAGE_NUMBER])
        epicgames.register(a.webdriver)
        a.webdriver.switch_to_window(a.webdriver.window_handles[YANDEX_PAGE_NUMBER])
        yandex.open_last_msg(a.webdriver)
        yandex._take_first_code(a.webdriver)


if __name__ == '__main__':
    farm = Farmer()
    farm.run()