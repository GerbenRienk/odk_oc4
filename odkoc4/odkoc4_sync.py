'''
Created on 20200123
based on the oc3 version
@author: Gerben Rienk
'''
import datetime
import json
import time

import logmailer

from utils.dictfile import readDictFile
from utils.general_functions import is_jsonable
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
    while True:
        # retrieve all study-subjects / participants from oc, using the api
        all_participants = api.participants.list_participants(data_def['studyOid'], aut_token, verbose=False)
        # now loop through the subjects / participants to check if the id - oid is still correct,
        # because this may have been changed in oc4 between cycles
        for one_participant in all_participants:
            util.subjects.check_and_update(one_participant['subjectKey'], one_participant['subjectOid'])
        
        # now loop through all the odk-tables in the data-definition
        for odk_table in data_def['odk_tables']:
            my_report.append_to_report('table: %s ' % odk_table['table_name'])

            # 1: start with retrieving the rows of this table
            odk_results = conn_odk.ReadDataFromOdkTable(odk_table['table_name'])
                        
            for odk_result in odk_results:
                # check if StudySubjectID from odk is already in oc
                add_subject_to_oc = True
                study_subject_id = odk_result[odk_table['id_field']]
                    
                # compare with all oc subjects / participants
                for one_participant in all_participants:
                    if(one_participant['subjectKey'] == study_subject_id):
                        # if we find a match, then set add_subject_to_db to False
                        add_subject_to_oc = False
                        
                if (add_subject_to_oc):
                    # try to add a subject / participant to oc4
                    add_result = api.participants.add_participant(data_def['studyOid'], data_def['siteOid'], study_subject_id, aut_token, verbose=False)
                    if (is_jsonable(add_result)):
                        # if we were successful we now have a json response, which we can use to add this subject to the util-db 
                        util.subjects.add_subject(add_result['subjectOid'], add_result['subjectKey'])
                    else:
                        # write unsuccessful ones in the report
                        my_report.append_to_report('trying to add study subject resulted in: %s\n' % add_result)
    
                    event_info = {"subjectKey":study_subject_id, "studyEventOID": data_def['studyEventOid'], "startDate":"2019-11-01", "endDate":"2019-11-01"}
                    schedule_result = api.events.schedule_event(data_def['studyOid'], data_def['siteOid'], event_info, aut_token, verbose=False)
                    my_report.append_to_report('try to schedule event: %s\n' % schedule_result)

                # now we have the subject in oc4 plus the event scheduled
                # we assume that we have the correct study subject oid in our util-db
                study_subject_oid = util.subjects.get_oid(study_subject_id)
                
                # for the administration of the following steps we need the uri
                uri = odk_result['_URI']
                util.uri.add(uri)
                
                # next step is to compose the odm-xml-file
                # start with creating it and writing the first, common tags
                file_name = 'odm_%s.xml' % study_subject_oid
                odm_xml = api.odm_parser(file_name, data_def['studyOid'], study_subject_oid, odk_table['eventOid'], odk_table['form_data'], odk_table['itemgroupOid'])
                
                # now loop through the odk-fields of the table and add them to the odm-xml
                all_odk_fields = odk_table['odk_fields']
                for odk_field in all_odk_fields:
                    odm_xml.add_item(odk_field['itemOid'], odk_result[odk_field['odk_column']], "")
                # write the closing tags
                odm_xml.close_file()
                
                # now submit the composed odm-xml file to the rest api
                #import_result = api.clinical_data.import_odm(aut_token, file_name, verbose=False)
                #print(import_result)
                
            '''                    
                # only import the data if this hasn't been done before
                if (not conn_util.UriComplete(odk_result['_URI'])):   
                    # now we should have the study subject id plus oid, so we can compose the odm for import                
                    study_subject_id = odk_result['GENERAL_INFORMATION_STUDY_SUBJECT_ID']
                    study_subject_oid = conn_util.DLookup('study_subject_oid', 'odkoc.study_subject_oc', 'study_subject_id=\'%s\'' % (study_subject_id))
                    complete_odm = compose_reader(study_subject_oid, odk_result)
    
                    import_results = myDataWS.importData(complete_odm)
                    # if our import was successful, then the result should start with Success
                    # and if so, we can mark this uri as complete
                    if (import_results.find('Success') == 0):
                        conn_util.MarkUriComplete(odk_result['_URI'], 'reader')
                    
                    my_report.append_to_report('reader ' + study_subject_id + ': ' + import_results)

            '''
        all_subjects=util.subjects.list() 
        for subject in all_subjects:
            print(subject[0], subject[1])
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
    
    my_report.append_to_report('finished looping from %s till %s.' % (start_time, current_time))
    # close the file so we can send it
    my_report.close_file()
    logmailer.MailThisLogFile('logs/report.txt')
    
    
if __name__ == '__main__':
    cycle_through_syncs()

