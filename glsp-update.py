# glsp-update.py

from datetime import datetime, timedelta               
from time import sleep

from selenium import webdriver                                                              
from selenium.webdriver.common.keys import Keys 
from bs4 import BeautifulSoup

from nflfantasy.glsp import getsess, Player


def _conv(v):
    try:
        return(float(v))
    except:
        return None
        
def _proj(driver, pos, created_at, yr, week):
    scr = "return document.getElementsByTagName('html')[0].innerHTML"
    html = driver.execute_script(scr)
    soup = BeautifulSoup(html, 'lxml')
    curmatch = driver.find_element_by_id('curmatch').text
    if curmatch:
        parts = [v.strip() for v in curmatch.split(' vs ')]
        player = parts[0]

    vals = [[td.text.strip() for td in tr.find_all('td')] for 
             tr in soup.find('div', {'id': 'fpg'}).find('tbody').find_all('tr')]
    return Player(name=player, pos=pos, created_at = created_at,
                  std_low = _conv(vals[0][1]), std_med=_conv(vals[1][1]), 
                  std_high=_conv(vals[2][1]), hppr_low = _conv(vals[0][2]), 
                  hppr_med=_conv(vals[1][2]), hppr_high=_conv(vals[2][2]),
                  ppr_low = _conv(vals[0][3]), ppr_med=_conv(vals[1][3]), 
                  ppr_high=_conv(vals[2][3]), yr=yr, week=week)

def add(sess, driver, pos, created_at, yr, week):
    p = _proj(driver, pos, created_at, yr, week)
    sess.add(p)
    try:
        sess.commit()
        logging.info('added {}'.format(p))
    except:
        sess.rollback()
        logging.exception('could not add {}'.format(p))

pos = 'WR'
yr = 2017
week = 17
created_at = datetime.now()
sess = getsess()
url = 'http://96.126.123.15/GLSPwr1/'
driver = webdriver.Firefox()

driver.get(url)
sleep(2)
add(sess, driver, pos, created_at, yr, week)
