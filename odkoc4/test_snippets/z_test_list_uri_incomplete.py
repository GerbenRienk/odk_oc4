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
        
    # we're finished with odk tables, so retrieve the job-logs from oc4, using the job uuid
    # but first we sleep a bit, to allow the oc-server to process the jobs
    print('just before incomplete')
    all_uris = util.uri.list_incomplete()
    print (len(all_uris))
    #print(all_uris[0])
    for one_uri in all_uris:
        
        # job uuid is in uri[6]
        uri = one_uri[0]
        print(uri + ' ' + one_uri[6])
        job_result = api.jobs.download_file(aut_token, one_uri[6], verbose=True)
        util.uri.write_import_result(uri, job_result)
        if(util.uri.has_import_errors(uri)):
            # something went wrong with our import, so report that
            my_report.append_to_report('errors in %s - %s' % (uri, one_uri[6]))
            my_report.append_to_report('log says: %s' % one_uri[7])
        else:
            # we didn't find errors, so mark the uri complete
            util.uri.set_complete(uri)
            # and delete the job from the server
            api.jobs.delete_file(aut_token, one_uri[6], verbose=False)
            # and delete the import file 
            file_name = 'request_files/' + one_uri[4]
            os.remove(file_name)
 
        # some book keeping to check if we must continue looping, or break the loop
        # first sleep a bit, so we do not eat up all CPU
        time.sleep(int(config['sleep_this_long']))
        current_time = datetime.datetime.now()
        difference = current_time - start_time
        loop_this_long = config['loop_this_long']
        max_diff_list = loop_this_long.split(sep=':') 
        max_difference = datetime.timedelta(hours=int(max_diff_list[0]), minutes=int(max_diff_list[1]), seconds=int(max_diff_list[2]))
        if difference > max_difference:
            break
    
    
    # close the file so we can send it
    my_report.close_file()
    # set up the mailer
    my_mailer = Mailer(config)
    # send the report
    my_mailer.send_file('logs/report.txt')
    
if __name__ == '__main__':
    cycle_through_syncs()

