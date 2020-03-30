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
    
    # for selecting the correct site, based on the first 7 characters of the study subject id, we need 
    # the dictionary with site mapping
    site_mapping = data_def['siteMapping']
    
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
        # retrieve all study-subjects / participants from oc4, using the api
        all_participants = api.participants.list_participants(data_def['studyOid'], aut_token, verbose=False)
        # now loop through the subjects / participants to check if the id - oid is still correct,
        # because this may have been changed in oc4 between cycles
        for one_participant in all_participants:
            util.subjects.check_and_update(one_participant['subjectKey'], one_participant['subjectOid'])
        
        # now loop through all the odk-tables in the data-definition
        for odk_table in data_def['odk_tables']:
            # 1: start with retrieving the rows of this table
            odk_results = conn_odk.ReadDataFromOdkTable(odk_table['table_name'])
                        
            for odk_result in odk_results:
                # check if StudySubjectID from odk is already in oc
                add_subject_to_oc = True
                study_subject_id = odk_result[odk_table['id_field']]
                #if we have no study subject id, then we'll take the uri
                if study_subject_id is None:
                    study_subject_id = odk_result['_URI']
                # find the site oid, based on the study subject id
                # set the site oid default to zero length string
                site_oid = 'no_site'
                for prefix, mapped_site_oid in site_mapping.items():
                    if (study_subject_id.find(prefix) == 0):
                        site_oid = mapped_site_oid
                
                if site_oid == 'no_site':
                    my_report.append_to_report('could not find a site for study subject %s in %s' % (study_subject_id, odk_table['table_name']))
                else:   
                    # compare with all oc subjects / participants
                    for one_participant in all_participants:
                        if(one_participant['subjectKey'] == study_subject_id):
                            # if we find a match, then set add_subject_to_db to False
                            add_subject_to_oc = False
                            
                    if (add_subject_to_oc):
                        # try to add a subject / participant to oc4
                        add_result = api.participants.add_participant(data_def['studyOid'], site_oid, study_subject_id, aut_token, verbose=False)
                        if (is_jsonable(add_result)):
                            new_participant = json.loads(add_result)
                            # if we were successful we now have a json response, which we can use to add this subject to the util-db 
                            util.subjects.add_subject(new_participant['subjectOid'], new_participant['subjectKey'])
                        else:
                            # write unsuccessful ones in the report
                            my_report.append_to_report('trying to add study subject resulted in: %s\n' % add_result)
                    
                    # by default set the serk to 0
                    serk = 0
                    # make a distinction between tables for events with a study-event-repeat-key and the rest
                    if 'serk' in odk_table:
                        serk = odk_result[odk_table['serk']]
                        event_info = {"subjectKey":study_subject_id, "studyEventOID": odk_table['eventOid'], "startDate":"1980-01-01", "endDate":"1980-01-01", "studyEventRepeatKey": serk}
                        while True:
                            # see if we can update the event with this serk
                            update_result = api.events.update_event(data_def['studyOid'], site_oid, event_info, aut_token, verbose=False)
                            # if we can, then the event exists and the status code will be 200
                            if update_result.status_code == 200:
                                break
                            # the serk does not exist, so we schedule an extra event and loop again to check if this was enough
                            schedule_result = api.events.schedule_event(data_def['studyOid'], site_oid, event_info, aut_token, verbose=False)
                        
                    else:
                        # for now, let's schedule the event anyway
                        event_info = {"subjectKey":study_subject_id, "studyEventOID": odk_table['eventOid'], "startDate":"1980-01-01", "endDate":"1980-01-01"}
                        schedule_result = api.events.schedule_event(data_def['studyOid'], site_oid, event_info, aut_token, verbose=False)
                        # the result may be none, when the event has already been scheduled
                        if(schedule_result):
                            if (is_jsonable(schedule_result)):
                                result = json.loads(schedule_result)
                                if(result['eventStatus']!='scheduled'):
                                    # report back errors
                                    my_report.append_to_report('try to schedule event: %s\n' % schedule_result)
    
                    # now we have the subject in oc4 plus the event scheduled
                    # we assume that we have the correct study subject oid in our util-db
                    study_subject_oid = util.subjects.get_oid(study_subject_id)
                    
                    # for the administration of the following steps we need the uri
                    uri = odk_result['_URI']
                    util.uri.add(uri, study_subject_oid)
                    
                    # only compose the odm and import, if the uri is not complete yet
                    if(not util.uri.is_complete(uri)):
                        # get the actual clinical data, so we know we can import or not
                        resp_clin_data = api.clinical_data.get_clinical_data(aut_token, data_def['studyOid'], study_subject_oid)
                        if (resp_clin_data.status_code == 200):
                            util.uri.set_clinical_data(uri, resp_clin_data.text)
                        
                        if (not util.uri.force_import(uri) and util.uri.has_data_in_itemgroup(uri, odk_table['eventOid'], odk_table['form_data']['FormOID'], odk_table['itemgroupOid'], serk, verbose=False)):
                            my_report.append_to_report(uri)
                            my_report.append_to_report('didn\'t submit data of %s for %s, because data exist in oc4 ' % (study_subject_id, odk_table['form_data']['FormName']))
                        else:
                            # no data in oc4 yet 
                            # next step is to compose the odm-xml-file
                            # start with creating it and writing the first, common tags
                            now = datetime.datetime.now()
                            time_stamp = now.strftime("%Y%m%d%H%M%S")
                            file_name = 'odm_%s_%s.xml' % (study_subject_oid, time_stamp)
                            odm_xml = api.odm_parser(file_name, data_def['studyOid'], study_subject_oid, odk_table['eventOid'], odk_table['form_data'], serk, verbose=True)
                            odm_xml.group_open(odk_table['itemgroupOid'])
                            # now loop through the odk-fields of the table and add them to the odm-xml
                            all_odk_fields = odk_table['odk_fields']
                            for odk_field in all_odk_fields:
                                odm_xml.add_item(odk_field['itemOid'], odk_result[odk_field['odk_column']], odk_field['item_type'])
                            # one last loop for multi selects
                            if 'multi_fields' in odk_table:
                                all_multi_fields = odk_table['multi_fields']
                                for multi_field in all_multi_fields:
                                    # mind that we use the uri to get all the selected values
                                    selected_values = conn_odk.GetMultiAnswers(multi_field['odk_table_name'], uri)
                                    odm_xml.add_multi_item(multi_field['itemOid'], selected_values)
                            # now close the ungrouped group
                            odm_xml.group_close()
                            
                            # check if we have repeating item groups
                            if 'repeating_item_groups' in odk_table:
                                all_rigs = odk_table['repeating_item_groups']
                                for one_rig in all_rigs:
                                    # get the fields so we can use them further down
                                    all_rig_odk_fields = one_rig['rig_odk_fields']
                                    rig_odk_results = conn_odk.ReadDataFromOdkTable(one_rig['rig_odk_table_name'], '"_PARENT_AURI"=\'%s\''  % uri, '"_ORDINAL_NUMBER"')
                                    for rig_odk_result in rig_odk_results:
                                        # for each occurrence, write an item group with an item group repeat key
                                        odm_xml.group_open(one_rig['rig_oid'], rig_odk_result['_ORDINAL_NUMBER'] )
                                        # loop through the fields
                                        for rig_odk_field in all_rig_odk_fields:
                                            odm_xml.add_item(rig_odk_field['itemOid'], rig_odk_result[rig_odk_field['odk_column']], rig_odk_field['item_type'])
                                           
                                        odm_xml.group_close()
                            # write the closing tags of the odm-file
                            odm_xml.close_file()
                            
                            # now submit the composed odm-xml file to the rest api
                            study_event_info = ''
                            if not serk == 0 :
                               study_event_info = ', event repeat key is %s' % serk 
                            my_report.append_to_report('submitting data of %s for %s%s' % (odk_table['form_data']['FormName'], study_subject_id, study_event_info))
                            import_job_id = api.clinical_data.import_odm(aut_token, file_name, verbose=False)
                            
                            # do the administration
                            util.uri.write_table_name(uri, odk_table['table_name'])
                            util.uri.write_odm(uri, file_name)
                            util.uri.write_job_id(uri, import_job_id)
                # next subject in the odk table
            # next odk table
        
        # we're finished with odk tables, so retrieve the job-logs from oc4, using the job uuid
        # but first we sleep a bit, to allow the oc-server to process the jobs
        time.sleep(int(config['sleep_this_long']))
        all_uris = util.uri.list_incomplete()
        
        for one_uri in all_uris:
            uri = one_uri[0]
            # job uuid is in uri[6]
            job_uuid = one_uri[6]
            if not job_uuid is None:
                job_result = api.jobs.download_file(aut_token, job_uuid, verbose=False)
                util.uri.write_import_result(uri, job_result)
                if(util.uri.has_import_errors(uri)):
                    # something went wrong with our import, so report that
                    my_report.append_to_report('\nerrors in %s - %s' % (uri, one_uri[6]))
                    my_report.append_to_report('log says: %s' % one_uri[7])
                else:
                    # we didn't find errors, so mark the uri complete
                    util.uri.set_complete(uri)
                    # and delete the job from the server
                    api.jobs.delete_file(aut_token, one_uri[6], verbose=False)
                    # and delete the import file 
                    file_name = 'request_files/' + one_uri[4]
                    # maybe the file was already removed, so check before trying to remove again
                    if os.path.isfile(file_name):
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
    
    my_report.append_to_report('\nfinished looping from %s till %s.' % (start_time, current_time))
    # close the file so we can send it
    my_report.close_file()
    # set up the mailer
    my_mailer = Mailer(config)
    # send the report
    my_mailer.send_file('logs/report.txt')
    
if __name__ == '__main__':
    cycle_through_syncs()

