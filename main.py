import random
import string
import selenium
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import errors


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
    def register(self, webdriver):
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
            raise errors.CaptchaFailedException('solve the captcha')
        print('')
    def open_last_msg(self, webdriver):
        webdriver.get('https://mail.yandex.ru/')
        first_message = webdriver.find_elements_by_class_name('js-messages-item-checkbox-controller')[0]
        print(first_message)
        print(dir(first_message))
        first_message.click()
    def _take_first_code(self, webdriver):
        code = webdriver.find_element_by_xpath(
            '//*[@id="nb-1"]/body/div[2]/div[5]/div/div[3]/div[3]/div[2]/div[5]/div[1]/div/div[3]/div/div/table/tbody/tr/td/center/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td/div')
        print(code)
        print(dir(code))
    def _take_2fa_code(self, webdriver):
        pass



class Epicgamesstore():
    def __init__(self, cls):
        self.__dict__ = cls.__dict__
    def register(self, webdriver, yandexmaildns='yandex.ru'):
        webdriver.get('https://www.epicgames.com/id/register')
        # webdriver.find_element_by_xpath('').send_keys('')
        webdriver.find_element_by_xpath('//*[@id="name"]').send_keys(self.firstname)
        webdriver.find_element_by_xpath('//*[@id="lastName"]').send_keys(self.lastname)
        webdriver.find_element_by_xpath('//*[@id="displayName"]').send_keys(self.epicgames_login)
        webdriver.find_element_by_xpath('//*[@id="email"]').send_keys(f'{self.login}@{yandexmaildns}')
        webdriver.find_element_by_xpath('//*[@id="password"]').send_keys(self.pswd)
        webdriver.find_element_by_xpath('//*[@id="termsOfService"]').click()
        webdriver.find_element_by_xpath('//*[@id="btn-submit"]').click()

class Farmer():
    def __init__(self, cls):
        self.__dict__ = cls.__dict__
    def run(self):
        pass


if __name__ == '__main__':
    a = BaseDataClass()
    yan = Yandex(a)
    epic = Epicgamesstore(a)
    yan.register(a.webdriver)
    epic.register(a.webdriver)
    yan.open_last_msg(a.webdriver)
