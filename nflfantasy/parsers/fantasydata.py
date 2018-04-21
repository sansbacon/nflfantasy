import logging

from bs4 import BeautifulSoup


class FantasyDataNFLParser():

    def __init__(self,**kwargs):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())


    def dst(self, content, season, week):
        '''
        Parses weekly page of DST scoring
        Args:
            content: HTML string

        Returns:
            list of dict
        '''
        results = []
        soup = BeautifulSoup(content, 'lxml')
        t = soup.find('table', {'id': 'StatsGrid'})
        if t:
            headers = []
            for th in t.find('tr').find_all('th'):
                try:
                    headers.append(th.text.lower().strip().replace(' ', '_'))
                except:
                    pass

            for tr in t.find_all('tr')[1:]:
                vals = []
                for td in tr.find_all('td'):
                    try:
                        vals.append(td.text)
                    except:
                        pass
                result = dict(zip(headers, vals))
                result['season_year'] = season
                result['week'] = week
                results.append(result)

        return results

if __name__ == '__main__':
    pass