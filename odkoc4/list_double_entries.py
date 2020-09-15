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
    my_report = Reporter('logs/list_double_entries.txt')
    config=readDictFile('odkoc4.config')
    if(config['environment'] == 'test'):
        with open('config/data_definition_test.json') as json_file:
            data_def = json.load(json_file)
    else:
        with open('config/data_definition_prod.json') as json_file:
            data_def = json.load(json_file)
    
    # create connections to the postgresql databases
    my_report.append_to_report("preparing connections")
    util = UtilDB(config, verbose=False)
    my_report.append_to_report('try to connect to util database, result: %s ' % util.init_result)
    conn_odk= ConnToOdkDB(config, verbose=False)
    my_report.append_to_report('try to connect to odk database, result: %s \n' % conn_odk.init_result)
        
        
    # now loop through all the odk-tables in the data-definition
    for odk_table in data_def['odk_tables']:
        
        double_entries = conn_odk.list_double_entries(odk_table['table_name'])
        process_this_subject = False
        for double_entry in double_entries:
            process_this_subject = False
            the_key_part = double_entry['STUDY_SUBJECT_ID'][7:9]
            if(config['environment'] == 'test' and the_key_part == '99'):
                process_this_subject = True
            if(config['environment'] == 'prod' and the_key_part != '99'):
                process_this_subject = True
            if process_this_subject:
                my_report.append_to_report('listing double entries in %s' % odk_table['form_data']['FormName'])
                my_report.append_to_report('%s %d' % (double_entry['STUDY_SUBJECT_ID'], double_entry['count']))

        '''
        all_itemgroups = odk_table['itemgroups']
        for item_group in all_itemgroups:
            all_odk_fields = item_group['odk_fields']
            for odk_field in all_odk_fields:
                my_report.append_to_report(odk_field['odk_column'] + '\t' + odk_field['itemOid'] + '\t' + odk_field['item_type'])

            # one last round for multi selects
            if 'multi_fields' in item_group:
                all_multi_fields = item_group['multi_fields']
                print('m')
                for multi_field in all_multi_fields:
                    my_report.append_to_report('multi: ' + multi_field['odk_table_name'] + '\t' + multi_field['itemOid'])

        if 'repeating_item_groups' in odk_table:
            all_repeating_item_groups = odk_table['repeating_item_groups']
            for repeating_item_group in all_repeating_item_groups:
                my_report.append_to_report('rig: ' + repeating_item_group['rig_odk_table_name'] + '\t' + repeating_item_group['rig_oid'])
                all_rig_odk_fields = repeating_item_group['rig_odk_fields']
                for rig_odk_field in all_rig_odk_fields:
                    my_report.append_to_report(rig_odk_field['odk_column'] + '\t' + rig_odk_field['itemOid'] + '\t' + rig_odk_field['item_type'])
       
        '''
if __name__ == '__main__':
    list_it()

