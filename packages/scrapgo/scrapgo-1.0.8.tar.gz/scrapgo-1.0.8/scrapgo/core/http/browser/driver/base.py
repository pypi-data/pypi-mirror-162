import time
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ChromeOptions

from .utils import source2response, set_browser_options, apply_settings



class WebDriverMixin:

    def sleep(self, delay=1):
        time.sleep(delay)

    def find_element(self, value, by=By.CSS_SELECTOR) -> WebElement:
        return super().find_element(by, value)
    
    def find_elements(self, value, by=By.CSS_SELECTOR) -> List[WebElement]:
        return super().find_elements(by, value)
    
    def clear_browser_cache(self):
        self.command_executor._commands['SEND_COMMAND'] = ('POST', '/session/$sessionId/chromium/send_command')
        self.execute('SEND_COMMAND', dict(cmd='Network.clearBrowserCache', params={}))
    
    @property
    def response(self):
        return source2response(self.current_url, self.page_source)

    def __del__(self):
        self.quit()



def load_chrome_driver_service():
    manager = ChromeDriverManager()
    driver_path=manager.install()
    return Service(driver_path)


class ChromeDriver(WebDriverMixin, webdriver.Chrome):

    def __init__(self, *args, **kwargs):
        service = load_chrome_driver_service()
        options = set_browser_options(ChromeOptions(), **kwargs)
        super().__init__(*args, service=service, options=options)
        apply_settings(self, **kwargs)

