'''
Created on 20180818
extra support and a better name
@author: Gerben Rienk
'''

from utils.dictfile import readDictFile
from utils.pg_api import ConnToOdkUtilDB, ConnToOdkDB, PGSubject
    
if __name__ == '__main__':
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    
    # create connections to the postgresql databases
    print('testing connection(s) to the database(s)')
    conn_util = ConnToOdkUtilDB(config, verbose=True)
    print()
    conn_odk= ConnToOdkDB(config, verbose=True)
    print()

