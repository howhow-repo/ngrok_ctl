import logging
import random
from decouple import config
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


logger = logging.getLogger(__name__)

class ApprtcController:
    browser = None
    room_id = None
    chromedriver = Service(config('DRIVERPATH', default='/usr/lib/chromium-browser/chromedriver'))

    @classmethod
    def start(cls):
        if cls.browser is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 無視窗
            chrome_options.add_argument('use-fake-ui-for-media-stream')
            chrome_options.add_argument('--incognito')  # 無痕
            chrome_options.add_argument('--no-sandbox')  # 解決DevToolsActivePort檔案不存在的報錯
            cls.room_id = str(random.randint(100000000, 999999999))
            cls.browser = webdriver.Chrome(service=cls.chromedriver, options=chrome_options)
            try:
                cls.browser.get(f'https://talk.io/{cls.room_id}')
                # join_button = cls.browser.find_element(By.ID, 'confirm-join-button')
                # join_button.click()
            except Exception as e:
                logger.error(e)
                cls.stop()
                return False

        return cls.room_id

    @classmethod
    def stop(cls):
        if cls.browser is not None:
            # hangup_button = cls.browser.find_element(By.ID, 'hangup')
            # hangup_button.click()
            cls.browser.quit()
            cls.browser, cls.room_id = None, None


if __name__ == '__main__':
    room_id = ApprtcController.start()
    print(room_id)
    input()
    ApprtcController.stop()
