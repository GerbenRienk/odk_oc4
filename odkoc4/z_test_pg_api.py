'''
Created on 20180818
extra support and a better name
@author: Gerben Rienk
'''

from utils.dictfile import readDictFile
from utils.pg_api import ConnToOdkUtilDB, ConnToOdkDB, PGSubject
from utils.reporter import Reporter
    
if __name__ == '__main__':
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    my_report = Reporter()
    # create connections to the postgresql databases
    conn_util = ConnToOdkUtilDB(config, verbose=True)
    my_report.append_to_report('try to connect to util database, result: %s ' % conn_util.init_result)
    conn_odk= ConnToOdkDB(config, verbose=True)
    my_report.append_to_report('try to connect to odk database, result: %s ' % conn_odk.init_result)

