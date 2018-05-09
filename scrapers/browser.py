# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import json
import logging
import os

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.errorhandler import WebDriverException


class BrowserScraper():


    def __init__(self, profile=None, visible=False):
        '''
        Scraper using selenium

        Args:
            profile: string, path to firefox profile, e.g. $HOME/.mozilla/firefox/6h98gbaj.default'    
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        if not visible:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()
        caps = DesiredCapabilities.FIREFOX.copy()
        caps['marionette'] = True
        if profile:
            self.browser = webdriver.Firefox(capabilities=caps,
                                             firefox_profile=webdriver.FirefoxProfile(profile),
                                             log_path=os.devnull)
        else:
            self.browser = webdriver.Firefox(capabilities=caps, log_path=os.devnull)
        self.urls = []

    def get(self, url, payload=None):
        '''
        Gets page using headless firefox
        
        Args:
            url: string

        Returns:
            string of HTML
        '''
        if payload:
            try:
                from urllib.parse import urlparse, urlencode
            except ImportError:
                from urlparse import urlparse
            url = '{}?{}'.format(url, urlencode(payload))

        self.browser.get(url)
        self.urls.append(url)
        return self.browser.page_source

    def get_json(self, url, payload=None):
        '''
        
        Args:
            url: 

        Returns:
            dict parsed json
        '''
        if payload:
            try:
                from urllib.parse import urlparse, urlencode
            except ImportError:
                from urlparse import urlparse
            url = '{}?{}'.format(url, urlencode(payload))

        try:
            self.browser.get(url)
            content = self.browser.find_element_by_tag_name('body').text
            return json.loads(content)
        except:
            logging.error('could not get {}'.format(url))
            return None

    def get_jsvar(self, varname):
        '''
        Gets python data structure of javascript variable

        Args:
            varname (str): name of javascript variable

        Returns:
            whatever the type of the javascript variable

        '''
        try:
            return self.browser.execute_script('return {};'.format(varname))
        except WebDriverException as e:
            logging.exception(e)
            return None


if __name__ == "__main__":
    pass