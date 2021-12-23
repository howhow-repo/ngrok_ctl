import logging
import time
import random
from decouple import config
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class ApprtcController:
    browser = None
    room_id = None
    chromedriver = Service(config('DRIVERPATH', default='/usr/lib/chromium-browser/chromedriver'))

    @classmethod
    def start(cls):
        if cls.browser is None:
            chrome_options = Options()
            # chrome_options.add_argument('--headless')  # 無視窗
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--use-fake-ui-for-media-stream')
            # chrome_options.add_argument('--incognito')  # 無痕
            chrome_options.add_argument('--no-sandbox')  # DevToolsActivePort
            # chrome_options.add_argument('--disable-gpu')

            cls.room_id = str(random.randint(100000000, 999999999))
            cls.browser = webdriver.Chrome(service=cls.chromedriver, options=chrome_options)

            try:
                cls.browser.get(f'https://talky.io/{cls.room_id}')
                ele_select = WebDriverWait(cls.browser, 100).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "/html/body/div[@id='root']"
                                                    "/div[1]/div[1]/div[1]/div[2]/div[3]/div[2]/label/select")))

                selects = Select(ele_select)
                selects.select_by_index(0)

                for i in range(10):
                    join_button = WebDriverWait(cls.browser, 100).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "/html/body/div[@id='root']"
                                                        "/div[1]/div[1]/div[1]/div[2]/div[3]/div[4]/button")))
                    if join_button.text == 'Join Call':
                        join_button.click()
                        break
                    else:
                        time.sleep(0.5)
                        pass

            except Exception as e:
                logger.error(e)
                cls.stop()
                return False

        return cls.room_id

    @classmethod
    def stop(cls):
        if cls.browser is not None:
            cls.browser.quit()
            cls.browser, cls.room_id = None, None


if __name__ == '__main__':
    room_id = ApprtcController.start()
    print(room_id)
    input()
    ApprtcController.stop()
