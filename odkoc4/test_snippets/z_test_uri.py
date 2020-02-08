'''
Created on 20180818
extra support and a better name
@author: Gerben Rienk
'''

from utils.dictfile import readDictFile
from utils.pg_api import UtilDB
    
if __name__ == '__main__':
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    
    # create connections to the postgresql databases
    util = UtilDB(config, verbose=False)
    
    new_uri = '2222'
    table_name = 'myt'
    odm_file_name = 'odm_SS_T456.xml' 
    job_uuid= '87785665'
    util.uri.add(new_uri)
    util.uri.write_table_name(new_uri, table_name)
    util.uri.write_odm(new_uri, odm_file_name)
    util.uri.write_job_id(new_uri, job_uuid)