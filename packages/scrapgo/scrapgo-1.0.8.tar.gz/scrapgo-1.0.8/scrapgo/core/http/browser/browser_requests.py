from scrapgo.settings import FromSettingsMixin
from scrapgo.lib import gen_random_value
from .driver.base import ChromeDriver



class ChromeBrowserRequests(FromSettingsMixin):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = self.apply_settings(
            ChromeDriver, setting_prefix='CHROME_'
        )

    def get_delay(self, delay):
        return delay or gen_random_value(*self.REQUEST_DELAY)
    
    def fetch(self, *args, **kwargs):
        url = kwargs.get('url')
        self.driver.get(url)
        return self.driver.response
