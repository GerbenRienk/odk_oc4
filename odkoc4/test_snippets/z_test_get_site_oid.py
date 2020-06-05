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
    
    study_subject_id = 'AM00102003'
    
    site_mapping = data_def['siteMapping']
    site_oid = ''
    for prefix, mapped_site_oid in site_mapping.items():
        if (study_subject_id.find(prefix) == 0):
            site_oid = mapped_site_oid
        
    print(site_oid)
    
    # our cycle starts here and ends at the break
    my_report.append_to_report('cycle started at %s\n' % str(start_time))
    
            
    # close the file so we can send it
    my_report.close_file()
    # set up the mailer
    my_mailer = Mailer(config)
    # send the report
    my_mailer.send_file('logs/report.txt')
    
if __name__ == '__main__':
    cycle_through_syncs()

