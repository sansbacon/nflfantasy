import logging
from pathlib import Path
import time

from requests_html import HTMLSession

from nflfantasy.parsers.ffc import *

s = HTMLSession()
ffcp = FFCParser()
pth = Path.home() / 'ffc'
url = 'https://fantasyfootballcalculator.com/draft/'                                  

proxies = {
    'http': 'socks5://localhost:9050',                                                                 
    'https': 'socks5://localhost:9050'
}  

logger = logging.getLogger()
fh = logging.FileHandler('ffc.log')
fh.setLevel(logging.ERROR)
logger.addHandler(fh)                                    
                                                
for id in range(4250000,4370000):
    print('starting {}'.format(id))                  
    try:                                                            
        fn = pth / '{}.htm'.format(id)
        if fn.is_file():
            print('skipping {}'.format(id))
            continue
        r = s.get(url.format(id), proxies=proxies)
        h1 = r.html.find('h1').text
        for txt in ['Dynasty', 'Not Found', 'QB']:
            if txt in h1:
                continue
        with open(fn.format(id), 'w') as f:               
            f.write(r.html.find('body').html())
            print('wrote {} to file'.format(id))                                                 
    except:
        logging.exception('could not get {}'.format(id))
    time.sleep(.1)  
