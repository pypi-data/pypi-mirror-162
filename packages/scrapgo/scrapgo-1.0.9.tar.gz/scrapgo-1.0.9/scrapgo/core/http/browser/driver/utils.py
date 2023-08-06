from mimetypes import guess_type

from selenium import webdriver
from requests.models import Response


def set_browser_options(options, browser_options:list=None, browser_experimental_options:dict=None, **kwargs):
    for opt in browser_options or []:
        options.add_argument(opt)
    for opt, value in (browser_experimental_options or {}).items():
        options.add_experimental_option(opt, value)
    return options


def apply_settings(driver:webdriver, browser_settings:dict=None, **kwargs):
    for conf, values in (browser_settings or {}).items():
        getattr(driver, conf)(*values)


def source2response(url, page_source):
    response = Response()
    response.url = url
    response.status_code = 200
    response._content = page_source.encode('utf-8')
    response.headers = {
        'Content-Type': guess_type(url)
    }
    return response

