import random
import string
import selenium
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import errors

import logging

YANDEX_PAGE_NUMBER = 2
EPICGAMES_PAGE_NUMBER = 1

logging.basicConfig(filename="farm.log", level=logging.INFO, filemode='a')
class BaseDataClass():
    def __init__(self):
        self.webdriver = Chrome()
        self.firstname = ''.join(random.choice(string.ascii_lowercase) for i in range(9))
        self.lastname = ''.join(random.choice(string.ascii_lowercase) for i in range(9))
        self.login = f'{self.firstname}firstrev{self.lastname}'
        self.pswd = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(18))
        self.epicgames_login = self.login[:15]


class Yandex():
    def __init__(self, cls):
        self.__dict__ = cls.__dict__
        self.page_number = YANDEX_PAGE_NUMBER-1
    def register(self, webdriver):
        webdriver.switch_to_window(self.tabs[self.page_number])
        webdriver.get('https://passport.yandex.ru/registration/mail')
        # may include verification of a phone number or email
        try:
            wait_for_page_load = WebDriverWait(webdriver, 4).until(EC.url_contains("registration/mail"))
        except selenium.common.exceptions.TimeoutException:
            raise errors.BadIpRequestException('Try to change proxy or wait')

        # webdriver.find_element_by_xpath('').send_keys('')
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
            wait_for_element = WebDriverWait(webdriver, 300).until(EC.url_contains("avatar"))
        except selenium.common.exceptions.TimeoutException:
            raise errors.CaptchaFailedException('solve the captcha yandex.ru')
        print('')
    def open_last_msg(self, webdriver):
        webdriver.switch_to_window(self.tabs[self.page_number])
        webdriver.get('https://mail.yandex.ru/')
        first_message = webdriver.find_elements_by_class_name('js-messages-item-checkbox-controller')[0]
        first_message.click()
    def _take_first_code(self, webdriver):
        webdriver.switch_to_window(self.tabs[self.page_number])
        webdriver.implicitly_wait(5)
        webdriver.find_element_by_xpath(
            '//*[@id="nb-1"]/body/div[9]/div/div/div/div/div/div/div/div[2]/div[4]/button[1]').click()
        code = webdriver.find_element_by_xpath(
            '//*[@id="nb-1"]/body/div[2]/div[5]/div/div[3]/div[3]/div[2]/div[5]/div[1]/div/div[3]/div/div/table/tbody/tr/td/center/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td/div')
        code.get_attribute()
    def _take_2fa_code(self, webdriver):
        webdriver.switch_to_window(self.tabs[self.page_number])
        pass



class Epicgamesstore():
    def __init__(self, cls):
        self.__dict__ = cls.__dict__
        self.page_number = EPICGAMES_PAGE_NUMBER-1
    def register(self, webdriver, yandexmaildns='yandex.ru'):
        webdriver.switch_to_window(self.tabs[self.page_number])
        webdriver.get('https://www.epicgames.com/id/register')
        try:
            wait_for_element = WebDriverWait(webdriver, 300).until(EC.visibility_of_element_located((By.ID, 'name')))
        except selenium.common.exceptions.TimeoutException:
            raise errors.CaptchaFailedException('solve the captcha epicgames')

        # webdriver.find_element_by_xpath('').send_keys('')
        webdriver.find_element_by_xpath('//*[@id="name"]').send_keys(self.firstname)
        webdriver.find_element_by_xpath('//*[@id="lastName"]').send_keys(self.lastname)
        webdriver.find_element_by_xpath('//*[@id="displayName"]').send_keys(self.epicgames_login)
        webdriver.find_element_by_xpath('//*[@id="email"]').send_keys(f'{self.login}@{yandexmaildns}')
        webdriver.find_element_by_xpath('//*[@id="password"]').send_keys(self.pswd)
        webdriver.find_element_by_xpath('//*[@id="termsOfService"]').click()
        wait_for_element = WebDriverWait(webdriver, 300).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-submit"]')))
        webdriver.find_element_by_xpath('//*[@id="btn-submit"]').click()

class Farmer():
    def __init__(self, cls):
        self.__dict__ = cls.__dict__
    def run(self):
        pass


if __name__ == '__main__':
    a = BaseDataClass()
    a.open_new_tab()
    a.get_all_atributes()
    yan = Yandex(a)
    epic = Epicgamesstore(a)
    epic.register(a.webdriver)

    wait_for_element = WebDriverWait(a.webdriver, 300).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="code"]')))
    # yan.register(a.webdriver)
    # yan.open_last_msg(a.webdriver)
    # yan._take_first_code(a.webdriver)
