'''
Created on 20180818
extra support and a better name
@author: Gerben Rienk
'''

from utils.dictfile import readDictFile
from utils.pg_api2 import UtilDB
    
if __name__ == '__main__':
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    
    # create connections to the postgresql databases
    util = UtilDB(config, verbose=True)
    t=util.subjects.list_subjects() 
    print(type(t))
    for row in t:
        print(row[0], row[1])
    
