import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class ApprtcController:
    browser = None
    room_id = None
    chromedriver = Service('/usr/lib/chromium-browser/chromedriver')

    @classmethod
    def start(cls):
        if cls.browser is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('use-fake-ui-for-media-stream')

            cls.room_id = str(random.randint(100000000, 999999999))
            cls.browser = webdriver.Chrome(service=cls.chromedriver, options=chrome_options)
            cls.browser.get(f'https://appr.tc/r/{cls.room_id}')
            join_button = cls.browser.find_element(By.ID, 'confirm-join-button')
            join_button.click()

        return cls.room_id

    @classmethod
    def stop(cls):
        if cls.browser is not None:
            cls.browser.quit()
            cls.room_id = None


if __name__ == '__main__':
    room_id = ApprtcController.start()
    print(room_id)
    time.sleep(10)
    ApprtcController.stop()