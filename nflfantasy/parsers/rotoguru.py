import logging

from bs4 import BeautifulSoup


class RotoguruNFLParser(object):

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def dfs_week(self, content):
        '''
        Parses weekly dfs results (ssv content wrapped by <pre>)       

        Args:
            content: 

        Returns:

        '''
        vals = []
        soup = BeautifulSoup(content, 'lxml')
        for pre in soup.findAll('pre'):
            if 'Week;Year' in pre.text:
                rows = pre.text.split('\n')
                headers = [item.strip().lower().replace(' ', '_').replace('/', '') for item in rows[0].split(';')]
                for row in rows[1:]:
                    sal = dict(list(zip(headers, row.split(';'))))
                    if sal.get('salary', None):
                        sal['salary'] = re.sub("[^0-9]", "", sal['salary'])
                    vals.append(sal)
        return vals

if __name__ == "__main__":
    pass
