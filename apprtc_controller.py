import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ApprtcController:
    browser = None
    room_id = None
    chromedriver = '/usr/lib/chromium-browser/chromedriver'

    @classmethod
    def start(cls):
        if cls.room_id is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('use-fake-ui-for-media-stream')

            cls.room_id = str(random.randint(100000000, 999999999))
            cls.browser = webdriver.Chrome(executable_path=cls.chromedriver, options=chrome_options)
            cls.browser.get(f'https://appr.tc/r/{cls.room_id}')
            join_button = cls.browser.find_element('confirm-join-button')
            join_button.click()

        return cls.room_id

    @classmethod
    def stop(cls):
        if cls.browser is not None:
            cls.browser.quit()
            cls.room_id = None
