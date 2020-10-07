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

def check_it():
    my_report = Reporter()
    config=readDictFile('odkoc4.config')
    with open('config/data_definition_prod.json') as json_file:
        data_def = json.load(json_file)
    
    # create connections to the postgresql databases
    my_report.append_to_report("preparing connections")
    util = UtilDB(config, verbose=False)
    my_report.append_to_report('try to connect to util database, result: %s ' % util.init_result)
    conn_odk= ConnToOdkDB(config, verbose=False)
    my_report.append_to_report('try to connect to odk database, result: %s \n' % conn_odk.init_result)
        
    #print(util.subjects.check_enrol('SS_AM001050_2213', verbose=True)) 
    #print(util.subjects.check_enrol('SS_AM001060_746', verbose=True)) 
    print(util.subjects.check_enrol('SS_AM001030_4221', verbose=True)) 
   

    # retrieve all candidates for check
    all_check_enrol = util.subjects.list_check_enrol()
    for check_enrol in all_check_enrol:
        study_subject_id=check_enrol[0]
        study_subject_oid=check_enrol[1]
        # check if we can find the enrollment in clinical data
        if util.subjects.check_enrol(study_subject_oid) == True:
            util.subjects.set_enrol_ok(study_subject_oid)
        else:
            my_report.append_to_report('data were imported for %s, but the subject is not enrolled' % study_subject_id)
            util.subjects.set_report_date(study_subject_oid)
        
    # if you find enrol = 1 set enrol_ok = true
    
    # else add to the report and set set report date to now
        
        
if __name__ == '__main__':
    check_it()

