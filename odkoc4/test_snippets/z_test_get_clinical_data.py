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
    api = OC4Api(config['apiUrl'])
    aut_token = api.sessions.get_authentication_token(config['autApiUrl'], config['oc4_username'], config['oc4_password'])
    
    # create connections to the postgresql databases
    my_report.append_to_report("preparing connections")
    util = UtilDB(config, verbose=False)
    my_report.append_to_report('try to connect to util database, result: %s ' % util.init_result)
    conn_odk= ConnToOdkDB(config, verbose=False)
    my_report.append_to_report('try to connect to odk database, result: %s \n' % conn_odk.init_result)
    
    # our cycle starts here and ends at the break
    my_report.append_to_report('cycle started at %s\n' % str(start_time))
    
    study_oid = data_def['studyOid']
    subjects_in_util = util.subjects.list()
    for subject in subjects_in_util:
        study_subject_oid = subject[1];
        clinical_data_in_oc4 = api.clinical_data.get_clinical_data(aut_token, study_oid, study_subject_oid)
        print(util.subjects.set_clinical_data(study_subject_oid, clinical_data_in_oc4))
        
    # close the file so we can send it
    my_report.close_file()
    # set up the mailer
    my_mailer = Mailer(config)
    # send the report
    my_mailer.send_file('logs/report.txt')
    
if __name__ == '__main__':
    cycle_through_syncs()

