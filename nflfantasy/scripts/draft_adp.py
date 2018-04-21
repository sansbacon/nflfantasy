# draft_adp.py

import webbrowser
import os
try:
    from urllib import pathname2url  # Python 2.x
except:
    from urllib.request import pathname2url  # Python 3.x

import pandas as pd
from nfl.utility import getdb


def html_table(fn, df):
    '''
    Outputs an html table
    
    Args:
        fn (str): filename to save 
        df (DataFrame): the dataframe to create html from

    Returns:
        None

    '''
    page = '''<html>
              <head>
                <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/dt-1.10.16/datatables.min.css"/>
                <script src="https://code.jquery.com/jquery-3.3.1.min.js" 
                  integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
              </head>
              <body>
                  <script type="text/javascript" src="https://cdn.datatables.net/v/dt/dt-1.10.16/datatables.min.js"></script>
                  <script type="text/javascript" src="https://cdn.datatables.net/1.10.16/js/dataTables.bootstrap.min.js"></script>
                  <script type="text/javascript">
                    $(document).ready(function() {
                      $('#draft').DataTable( {
                        "iDisplayLength": 100,  
                        "order": [|idx|, 'desc'],
                        "columnDefs": [
                            {"className": "dt-center", "targets": "_all"}
                          ]
                      } );
                    } );
                  </script>
                  |TABLE|
              </body>
              </html>'''

    html = df.to_html(border=0,
                      index=False,
                      classes='compact display" id = "draft')

    with open(fn, 'w') as outfile:
        outfile.write(page.replace('|TABLE|', html).replace('|idx|', '4'))

def run():
    html = '/tmp/draft.html'
    db = getdb()
    q = """SELECT * FROM extra_dfs.draft_my_players"""
    df = pd.DataFrame(db.select_dict(q))
    col_order = ['first_name','last_name','position','n','ownpct',
                 'avgpick','high','low','myd_adp','myd_high','myd_low']
    html_table(html, df[col_order])
    url = 'file:{}'.format(pathname2url(os.path.abspath(html)))
    webbrowser.open_new(url)


if __name__ == '__main__':
    run()
