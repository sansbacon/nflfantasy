import hashlib
import logging
import os
import time

import requests


class FootballScraper(object):

    def __init__(self, headers=None, cookies=None, cache_name=None, delay=1, expire_hours=168, as_string=False, proxies=None):
        '''
        Base class for common scraping tasks
        Args:
            headers: dict of headers
            cookies: cookiejar object
            cache_name: should be full path
            delay: int (be polite!!!)
            expire_hours: int - default 168
            as_string: get string rather than parsed json
            proxies: dict of proxies
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        if not cookies:
            try:
                import cookielib
                cookies = cookielib.MozillaCookieJar()
            except (NameError, ImportError) as e:
                try:
                    import http.cookiejar
                    cookies = http.cookiejar.MozillaCookieJar()
                except Exception as e:
                    pass

        _s = requests.Session()
        _s.cookies = cookies
        if proxies:
            _s.proxies = proxies

        if headers:
            _s.headers.update(headers)
        else:
            _s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'})

        if cache_name:
            if not '/' in cache_name:
                cache_name = os.path.join('/tmp', cache_name)
            try:
                from cachecontrol import CacheControlAdapter
                from cachecontrol.heuristics import ExpiresAfter
                from cachecontrol.caches import FileCache
                _s.mount('http://', CacheControlAdapter(cache=FileCache(cache_name), cache_etags = False,
                                                        heuristic=ExpiresAfter(hours=expire_hours)))
            except ImportError as e:
                try:
                    import requests_cache
                    requests_cache.install_cache(cache_name)
                except:
                    pass
        self.s = _s
        self.urls = []
        self.as_string = as_string
        if delay > 0:
            self.delay = delay
        else:
            self.delay = None

    def get(self, url, payload=None, encoding='utf-8'):
        '''

        Args:
            url:
            payload:
            encoding:

        Returns:

        '''
        if payload:
            r = self.s.get(url, params={k:payload[k] for k in sorted(payload)})
        else:
            r = self.s.get(url)
        self.urls.append(r.url)
        r.raise_for_status()
        logging.debug(r.status_code)
        logging.debug(r.headers)
        if self.delay:
            time.sleep(self.delay)
        return r.content.decode(encoding)

    def get_filecache(self, url, savedir='/tmp', encoding='utf-8'):
        '''
        Uses file-based caching, helpful for debugging because can look at files
        Args:
            url:
            savedir:
            encoding:

        Returns:
            content: HTML string
        '''
        fn = os.path.join(savedir, '{}.html'.format(hashlib.md5(url).hexdigest()))
        if os.path.exists(fn):
            with open(fn, 'rb') as infile:
                content = infile.read()
        else:
            r = self.s.get(url)
            self.urls.append(r.url)
            r.raise_for_status()
            content = r.content.decode(encoding)
            with open(fn, 'wb') as outfile:
                outfile.write(content)
            if self.delay:
                time.sleep(self.delay)
        return content

    def get_json(self, url, payload=None):
        '''
        Gets JSON resource and (default) parses into python data structure
        Args:
            url:
            payload: query string parameters

        Returns:
            parsed JSON or JSON string
        '''
        if payload:
            r = self.s.get(url, params={k:payload[k] for k in sorted(payload)})
            logging.debug(r.status_code)
            logging.debug(r.headers)
        else:
            r = self.s.get(url, params=None)
        self.urls.append(r.url)
        r.raise_for_status()
        logging.debug(r.status_code)
        logging.debug(r.headers)
        if self.delay:
            time.sleep(self.delay)
        if self.as_string:
            return r.content
        else:
            return r.json()

    def post(self, url, payload):
        '''

        Args:
            url:
            payload:

        Returns:

        '''
        if payload:
            r = self.s.get(url, params={k:payload[k] for k in sorted(payload)})
        else:
            r = self.s.get(url)
        self.urls.append(r.url)
        r.raise_for_status()
        if self.delay:
            time.sleep(self.delay)
        return r.content

if __name__ == "__main__":
    pass
