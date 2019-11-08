'''
Created on 20180818

@author: GerbenRienk
'''
from utils.dictfile import readDictFile
from utils.pg_api import ConnToOdkUtilDB

def test_it():
    print('start')
    config=readDictFile('odkoc.config')
    conn_util = ConnToOdkUtilDB()    
    #conn_util.MarkUriComplete('uri2')
    print(conn_util.UriComplete('uri4'))
    print('end')
    
if __name__ == '__main__':
    test_it()
