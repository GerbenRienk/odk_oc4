'''
Created on 20200123
based on the oc3 version
@author: Gerben Rienk
'''
import datetime
import json
import time
import os

from utils.dictfile import readDictFile
from utils.general_functions import is_jsonable
#from utils.logmailer import Mailer
#from utils.oc4_api import OC4Api
from utils.pg_api import UtilDB, ConnToOdkDB
from utils.reporter import Reporter

from _operator import itemgetter

def list_it():
    my_report = Reporter()
    config=readDictFile('odkoc4.config')
    with open('config/data_definition.json') as json_file:
        data_def = json.load(json_file)
    
    # create connections to the postgresql databases
    my_report.append_to_report("preparing connections")
    util = UtilDB(config, verbose=False)
    my_report.append_to_report('try to connect to util database, result: %s ' % util.init_result)
    conn_odk= ConnToOdkDB(config, verbose=False)
    my_report.append_to_report('try to connect to odk database, result: %s \n' % conn_odk.init_result)
        
        
    # now loop through all the odk-tables in the data-definition
    for odk_table in data_def['odk_tables']:
        my_report.append_to_report('\n' + odk_table['table_name'])
        all_odk_fields = odk_table['odk_fields']
        for odk_field in all_odk_fields:
            my_report.append_to_report(odk_field['odk_column'] + '\t' + odk_field['itemOid'] + '\t' + odk_field['item_type'])
        # one last round for multi selects
        if 'multi_fields' in odk_table:
            all_multi_fields = odk_table['multi_fields']
            for multi_field in all_multi_fields:
                print(multi_field['itemOid'])

        if 'repeating_item_groups' in odk_table:
            all_repeating_item_groups = odk_table['repeating_item_groups']
            for repeating_item_group in all_repeating_item_groups:
                print(multi_field['itemOid'])
        
        # repeating_item_groups
        
        
if __name__ == '__main__':
    list_it()

