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

from utils.oc4_api import OC4Api
from utils.pg_api import UtilDB, ConnToOdkDB

from _operator import itemgetter

if __name__ == '__main__':
    # we need a fake study_subject_oid
    study_subject_oid = 'Fake'
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    # read configuration file for tables, fields and oc4 oid's
    with open('config/data_definition.json') as json_file:
        data_def = json.load(json_file)

    # start with requesting an authentication token, which we can use for some time
    api = OC4Api(config['apiUrl'])
    aut_token = api.sessions.get_authentication_token(config['autApiUrl'], config['oc4_username'], config['oc4_password'])
    
    # create connections to the postgresql databases
    #util = UtilDB(config, verbose=False)
    conn_odk= ConnToOdkDB(config, verbose=False)
    
    # our cycle starts here and ends at the break

    # now loop through all the odk-tables in the data-definition
    for odk_table in data_def['odk_tables']:
        # 1: start with retrieving the rows of this table
        odk_results = conn_odk.ReadDataFromOdkTable(odk_table['table_name'])
        print(odk_table['table_name'])            
        for odk_result in odk_results:
            # check if StudySubjectID from odk is already in oc
            add_subject_to_oc = True
            study_subject_id = odk_result[odk_table['id_field']]
                            
            # next step is to compose the odm-xml-file
            # start with creating it and writing the first, common tags
            now = datetime.datetime.now()
            time_stamp = now.strftime("%Y%m%d%H%M%S")
            file_name = 'odm_%s_%s.xml' % (study_subject_oid, time_stamp)
            odm_xml = api.odm_parser(file_name, data_def['studyOid'], study_subject_oid, odk_table['eventOid'], odk_table['form_data'], odk_table['itemgroupOid'])
            
            # now loop through the odk-fields of the table and add them to the odm-xml
            all_odk_fields = odk_table['odk_fields']
            for odk_field in all_odk_fields:
                # print(odk_field['odk_column'])
                odm_xml.add_item(odk_field['itemOid'], odk_result[odk_field['odk_column']], odk_field['item_type'])
            # write the closing tags
            odm_xml.close_file()
            