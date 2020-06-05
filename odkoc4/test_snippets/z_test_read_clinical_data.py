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
from utils.logmailer import Mailer
from utils.oc4_api import OC4Api
from utils.pg_api import UtilDB, ConnToOdkDB
from utils.reporter import Reporter

from _operator import itemgetter

def cycle_through_syncs():
    # we start by reading the config file and preparing the connections to the databases 
    my_report = Reporter()
    start_time = datetime.datetime.now()
    
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    # read configuration file for tables, fields and oc4 oid's
    with open('config/data_definition.json') as json_file:
        data_def = json.load(json_file)

    # start with requesting an authentication token, which we can use for some time
    api     = OC4Api(config['apiUrl'])
    aut_token = api.sessions.get_authentication_token(config['autApiUrl'], config['oc4_username'], config['oc4_password'])
    
    # create connections to the postgresql databases
    my_report.append_to_report("preparing connections")
    util = UtilDB(config, verbose=False)
    my_report.append_to_report('try to connect to util database, result: %s ' % util.init_result)
    conn_odk= ConnToOdkDB(config, verbose=False)
    my_report.append_to_report('try to connect to odk database, result: %s \n' % conn_odk.init_result)
    
    # our cycle starts here and ends at the break
    my_report.append_to_report('cycle started at %s\n' % str(start_time))
    
    # "uuid:01c8899f-50a3-4d4e-949e-c05df8fe497e"
    this_event_oid = 'SE_IMPEV'
    this_form_oid = 'F_VS'
    this_item_group_oid = 'IG_VS_VITAL_SIGNS_GRP'
    
    
    all_uris = util.uri.list()
    for one_uri in all_uris:
        uri = one_uri[0]
        if (util.uri.has_data_in_itemgroup(uri, this_event_oid, this_form_oid, this_item_group_oid)):
            print('data present for %s' % uri)
        else:
            print('no data present for %s' % uri)
            
        '''
        cd_json = json.loads(util.uri.get_clinical_data(uri)[0][0])
        se_data = cd_json['ClinicalData']['SubjectData']['StudyEventData']
        print(cd_json['ClinicalData']['SubjectData']['@OpenClinica:StudySubjectID'])
        
        # a subject can have one event or more
        if (type(se_data) is dict):
            if (se_data['@StudyEventOID'] == this_event_oid):
                form_data = se_data['FormData']
            
        if (type(se_data) is list):
            for one_event in se_data:
                if (one_event['@StudyEventOID'] == this_event_oid):
                    form_data = one_event['FormData']
                
        # first we must check if we have one form in the event, or more
        # set a flag to indicate that we have any groups at all to False
        groups_exist = False
        if (type(form_data) is dict):
            if (form_data['@FormOID'] == this_form_oid):
                item_group_data = form_data['ItemGroupData']
                groups_exist = True
                
        if (type(form_data) is list):
            for one_form in form_data:
                if (one_form['@FormOID'] == this_form_oid):
                    item_group_data = one_form['ItemGroupData']
                    groups_exist = True
        
        if (groups_exist):            
            # now we must check if this form has one item group or more
            if (type(item_group_data) is dict):
                if (item_group_data['@ItemGroupOID'] == this_item_group_oid):
                    item_group_data_exist = True
                    
            if (type(item_group_data) is list):
                for one_item_group in item_group_data:
                    if (one_item_group['@ItemGroupOID'] == this_item_group_oid):
                        item_group_data_exist = True
                    
        if (item_group_data_exist):
            print('data exist for %s %s %s' % (this_event_oid, this_form_oid, this_item_group_oid))
        
        '''    
            
    # close the file so we can send it
    my_report.close_file()
    # set up the mailer
    my_mailer = Mailer(config)
    # send the report
    my_mailer.send_file('logs/report.txt')
    
if __name__ == '__main__':
    cycle_through_syncs()

