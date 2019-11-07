'''
Created on 20180818
extra support and a better name
@author: GerbenRienk
'''
import time
import datetime
import logmailer
from utils.dictfile import readDictFile
from utils.ocwebservices import studySubjectWS, studyEventWS, dataWS
from utils.pg_api import ConnToOdkUtilDB, ConnToOdkDB, PGSubject
from utils.reporter import Reporter
from utils.ma006 import compose_lamp, compose_misca, compose_reader, compose_screening
from _operator import itemgetter

def cycle_through_syncs():
    # we start by reading the config file and preparing the connections to the databases 
    my_report = Reporter()
    start_time = datetime.datetime.now()
    my_report.append_to_report('cycle started at ' + str(start_time))
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc.config')

    # initialise the oc-webservices
    myWebService = studySubjectWS(config['userName'], config['password'], config['baseUrl'])
    myEventWS = studyEventWS(config['userName'], config['password'], config['baseUrl'])
    myDataWS = dataWS(config['userName'], config['password'], config['baseUrl'])

    # create connections to the postgresql databases
    conn_util = ConnToOdkUtilDB()
    my_report.append_to_report('try to connect to util database, result: %s ' % conn_util.init_result)
    conn_odk= ConnToOdkDB()
    my_report.append_to_report('try to connect to odk database, result: %s ' % conn_odk.init_result)
    
    # our cycle starts here and ends at the break
    while True:
        '''
        start with form READER
        '''
        # 1: start with retrieving the rows of odk-table HS_RDT_READER_1_V1_CORE
        odk_results = conn_odk.ReadDataFromOdkTable("odk_prod.\"HS_RDT_READER_1_V1_CORE\"")
        # for the study subject id look in:
        # odk_result['GENERAL_INFORMATION_STUDY_SUBJECT_ID']
            
        # 2: create subject in oc, if necessary
        # retrieve all StudySubjectEvents from oc, using the webservice
        allStudySubjectsInOC = myWebService.getListStudySubjects(config['studyIdentifier'])
        
        for odk_result in odk_results:
            # check if StudySubjectID from odk is already in oc
            add_subject_to_db = True
            study_subject_id = odk_result['GENERAL_INFORMATION_STUDY_SUBJECT_ID']
            # compare with all oc subjects events
            for studysubjectid_oc in allStudySubjectsInOC:
                if(studysubjectid_oc == study_subject_id):
                    add_subject_to_db = False
                    
            if (add_subject_to_db):
                # add study_subject_id to the oc
                add_results = myWebService.addStudySubject(config['studyIdentifier'], config['siteIdentifier'], study_subject_id)
                #print(add_results)
                # TODO: add error-handling for fail of creating subject 
                # and schedule the event
                study_subject_oid = myEventWS.scheduleEvent(config['studyIdentifier'], study_subject_id, config['studyEventOID'], 'def', '1980-01-01')
                #TODO: add errorhandling for fail of scheduling event 
                
                # now add the combination id oid to the util database
                # only add the pair if the oid starts with SS_
                if (study_subject_oid.find('SS_') == 0):
                    conn_util.AddSubjectToDB(study_subject_oid, study_subject_id)
            
            # extra check: maybe we somehow missed the study subject oid and then there will be no record in table study_subject_oc
            if (conn_util.DLookup('study_subject_oid', 'odkoc.study_subject_oc', 'study_subject_id=\'%s\'' % (study_subject_id)) == ''):
                new_subject = PGSubject(study_subject_id)
                conn_util.AddSubjectToDB(new_subject.GetSSOID(), study_subject_id)
                
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
        go on with with form SCREENING
        '''
        odk_results = conn_odk.ReadDataFromOdkTable("odk_prod.\"SCREEN19M__V3_CORE\"", 'not \"INFORMED_CONSENT_STUDY_SUBJECT_ID\" is null')
        # for the study subject id look in:
        # odk_result['INFORMED_CONSENT_STUDY_SUBJECT_ID']
            
        # 2: create subject in oc, if necessary
        # retrieve all StudySubjectEvents from oc, using the webservice
        allStudySubjectsInOC = myWebService.getListStudySubjects(config['studyIdentifier'])
        
        for odk_result in odk_results:
            # check if StudySubjectID from odk is already in oc
            add_subject_to_db = True
            study_subject_id = odk_result['INFORMED_CONSENT_STUDY_SUBJECT_ID']
            print(study_subject_id)
            # compare with all oc subjects events
            for studysubjectid_oc in allStudySubjectsInOC:
                if(studysubjectid_oc == study_subject_id):
                    add_subject_to_db = False
                    
            if (add_subject_to_db):
                # add study_subject_id to the oc
                add_results = myWebService.addStudySubject(config['studyIdentifier'], config['siteIdentifier'], study_subject_id)
                # TODO: add error-handling for fail of creating subject 
                # and schedule the event
                study_subject_oid = myEventWS.scheduleEvent(config['studyIdentifier'], study_subject_id,config['studyEventOID'], 'def', '1980-01-01')
                #TODO: add errorhandling for fail of scheduling event 
                
                # now add the combination id oid to the util database
                # only add the pair if the oid starts with SS_
                if (study_subject_oid.find('SS_') == 0):
                    conn_util.AddSubjectToDB(study_subject_oid, study_subject_id)

            # extra check: maybe we somehow missed the study subject oid and then there will be no record in table study_subject_oc
            if (conn_util.DLookup('study_subject_oid', 'odkoc.study_subject_oc', 'study_subject_id=\'%s\'' % (study_subject_id)) == ''):
                new_subject = PGSubject(study_subject_id)
                conn_util.AddSubjectToDB(new_subject.GetSSOID(), study_subject_id) 
                   
            print('we have study subject id %s and oid %s' % (study_subject_id, conn_util.DLookup('study_subject_oid', 'odkoc.study_subject_oc', 'study_subject_id=\'%s\'' % (study_subject_id)) ))
            print(odk_result['_URI'], conn_util.UriComplete(odk_result['_URI']))
            # only import the data if this hasn't been done before
            if (not conn_util.UriComplete(odk_result['_URI'])):  
                print('dive into it') 
                # now we should have the study subject id plus oid, so we can compose the odm for import                
                study_subject_id = odk_result['INFORMED_CONSENT_STUDY_SUBJECT_ID']
                study_subject_oid = conn_util.DLookup('study_subject_oid', 'odkoc.study_subject_oc', 'study_subject_id=\'%s\'' % (study_subject_id))
                complete_odm = compose_screening(study_subject_oid, odk_result)
                print (complete_odm)
                # we'll make an exception for I_MA006_OTHER_DISEASE_HX, because this is a group of check-boxes
                # in complete_odm we have a placeholder {OTHER_DISEASE_HX}
                parent_uri = odk_result['_URI']
                hx_results = conn_odk.ReadDataFromOdkTable("odk_prod.\"SCREEN19M__V3_MED_HISTO_CONCO_MED_OTHER_DISEASE_HX\"", '\"_PARENT_AURI\"=\'%s\'' % (parent_uri))
                other_disease_hx = ''
                for hx in hx_results:
                    other_disease_hx = other_disease_hx + hx['VALUE'] + ','
                    
                if (other_disease_hx != ''):
                    # take off the last comma
                    other_disease_hx = other_disease_hx[:-1]
                        
                # finally we can replace the placeholder with the actual values
                complete_odm = complete_odm.replace('{OTHER_DISEASE_HX}', other_disease_hx)
                
                # import the odm data
                import_results = myDataWS.importData(complete_odm)
                if (import_results.find('Success') != 0):
                    # if something went wrong, print it
                    print(import_results)
                    import_screening_core_success = False
                else:
                    # if our import was successful, then make a note of it    
                    import_screening_core_success = True
                    my_report.append_to_report('screening ' + study_subject_id + ': ' + import_results)
                
                '''    
                now we can look at the repeating item group for miscarriages
                '''
                
                odk_misca_results = conn_odk.ReadDataFromOdkTable("odk_prod.\"SCREEN19M__V3_OBSETRIC_INFO_EXAM_BABY_DIED\"", '\"_PARENT_AURI\"=\'%s\'' % (parent_uri))
                for misca in odk_misca_results:
                    # print('misca ' + parent_uri + ' ' + misca['_URI'])
                    complete_odm = compose_misca(study_subject_oid, misca)
                    import_results = myDataWS.importData(complete_odm)
                
                if (import_results.find('Success') != 0):
                    # if something went wrong, print it
                    print(import_results)
                    import_screening_misca_success = False
                else:
                    # if our import was successful, then make a note of it    
                    import_screening_misca_success = True
                    my_report.append_to_report('misca ' + study_subject_id + ': ' + import_results)
                    
                # now do the bookkeeping
                if (import_screening_core_success and import_screening_misca_success):
                    conn_util.MarkUriComplete(odk_result['_URI'], 'screening')
      
        '''
        go on with with form LAMP
        '''
        odk_results = conn_odk.ReadDataFromOdkTable("odk_prod.\"LAMP_TESTING_V1_CORE\"", 'not \"GENERAL_INFORMATION_STUDY_SUBJECT_ID\" is null')
        # for the study subject id look in:
        # odk_result['GENERAL_INFORMATION_STUDY_SUBJECT_ID']
            
        # 2: create subject in oc, if necessary
        # retrieve all StudySubjectEvents from oc, using the webservice
        allStudySubjectsInOC = myWebService.getListStudySubjects(config['studyIdentifier'])
        
        for odk_result in odk_results:
            # check if StudySubjectID from odk is already in oc
            add_subject_to_db = True
            study_subject_id = odk_result['GENERAL_INFORMATION_STUDY_SUBJECT_ID']
            # compare with all oc subjects events
            for studysubjectid_oc in allStudySubjectsInOC:
                if(studysubjectid_oc == study_subject_id):
                    add_subject_to_db = False
                    
            if (add_subject_to_db):
                # add study_subject_id to the oc
                add_results = myWebService.addStudySubject(config['studyIdentifier'], config['siteIdentifier'], study_subject_id)
                # TODO: add error-handling for fail of creating subject 
                # and schedule the event
                study_subject_oid = myEventWS.scheduleEvent(config['studyIdentifier'], study_subject_id,config['studyEventOID'], 'def', '1980-01-01')
                #TODO: add errorhandling for fail of scheduling event 
                
                # now add the combination id oid to the util database
                # only add the pair if the oid starts with SS_
                if (study_subject_oid.find('SS_') == 0):
                    conn_util.AddSubjectToDB(study_subject_oid, study_subject_id)

            # extra check: maybe we somehow missed the study subject oid and then there will be no record in table study_subject_oc
            if (conn_util.DLookup('study_subject_oid', 'odkoc.study_subject_oc', 'study_subject_id=\'%s\'' % (study_subject_id)) == ''):
                new_subject = PGSubject(study_subject_id)
                conn_util.AddSubjectToDB(new_subject.GetSSOID(), study_subject_id)    
            
            # only import the data if this hasn't been done before  
            if (not conn_util.UriComplete(odk_result['_URI'])):   
                # now we should have the study subject id plus oid, so we can compose the odm for import                
                study_subject_id = odk_result['GENERAL_INFORMATION_STUDY_SUBJECT_ID']
                study_subject_oid = conn_util.DLookup('study_subject_oid', 'odkoc.study_subject_oc', 'study_subject_id=\'%s\'' % (study_subject_id))
                complete_odm = compose_lamp(study_subject_oid, odk_result)
            
                import_results = myDataWS.importData(complete_odm)
                if (import_results.find('Success') != 0):
                    # if something went wrong, print it
                    print(import_results)
                    import_lamp_success = False
                else:
                    # if our import was successful, then make a note of it    
                    import_lamp_success = True
                    my_report.append_to_report('lamp ' + study_subject_id + ': ' + import_results)

                if (import_lamp_success):
                    conn_util.MarkUriComplete(odk_result['_URI'], 'lamp')
        
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
    #logmailer.MailThisLogFile('logs/report.txt')
    
    
if __name__ == '__main__':
    cycle_through_syncs()

#from utils.limesurveyrc2api import LimeSurveyRemoteControl2API
    # read with combinations of StudyEventOIDs and LimeSurvey sids
    #event_survey_pairs=readDictFile('event_survey_pairs')

        # 4: create the ws data
        
        # retrieve the subjects that we created earlier, using the connection to the postgresql database
        #subjects_in_db = conn.ReadSubjectsFromDB()
        
        # now all StudySubjects in OpenClinica are also in our postgresql-database
        # so we refresh our list 
        #subjects_in_db = conn.ReadSubjectsFromDB()
        
        # collecting LimeSurvey data
        # Make a session, which is a bit of overhead, but the script will be running for hours.
        #api = LimeSurveyRemoteControl2API(config['lsUrl'])
        #session_req = api.sessions.get_session_key(config['lsUser'], config['lsPassword'])
        #session_key = session_req.get('result')
                    
        # initialise a new list for all tokens of all surveys
        # so we can check if a new token must be created
        #all_tokens = []
        #for event_oid, sid in event_survey_pairs.items():
            #participants_req = api.tokens.list_participants(session_key, sid)
            #participants = participants_req.get('result')
            #for participant in participants:
                #loop through the participants, but only if there are any
                #if participant != 'status':
                    #p_info = participant.get('participant_info')
                    #all_tokens.append( (p_info.get('firstname'), event_oid, sid, participant.get('token'), participant.get('completed')))
                    
        
        #for studysubject_event in allStudySubjectEvents:  
            # check if we must check this event
            #if studysubject_event[1] in event_survey_pairs:
                # yes, we must check this event 
                #blnAddTokens = True
                #for one_token in all_tokens:
                    #if one_token[0] == studysubject_event[0] and one_token[1] == studysubject_event[1]:
                        # a token exists
                        #blnAddTokens = False
        
                #if blnAddTokens:
                    #self._logger.debug("add token for " + studysubject_event[0] + ", " + studysubject_event[1])
                    #print ("add token for " + studysubject_event[0] + " " + str(event_survey_pairs[studysubject_event[1]]) + ", " + studysubject_event[1])
                    #participant_data = {'firstname': studysubject_event[0]}
                    #add_participant_req = 
                    #api.tokens.add_participants(session_key, event_survey_pairs[studysubject_event[1]], participant_data)
                    #my_report.append_to_report('created token for survey %s for subject %s' % (sid, studysubject_event[0]))
        
        # we may have added tokens, so refresh all_tokens
        # TODO: lets's make this a method
        #all_tokens = []
        #for event_oid, sid in event_survey_pairs.items():
            #participants_req = api.tokens.list_participants(session_key, sid)
            #participants = participants_req.get('result')
            #for participant in participants:
                # loop through the participants, but only if there are any
                #if participant != 'status':
                    #p_info = participant.get('participant_info')
                    #all_tokens.append( (p_info.get('firstname'), event_oid, sid, participant.get('token'), participant.get('completed')))      

        # now import the LimeSurvey results into OpenClinica 
        # sorted by study subject id
        #sorted_tokens = sorted(all_tokens, key=itemgetter(0))
        #last_ssid = 'x'
        #lime_survey_header = 'ev. token  completed&#10;---------------------------&#10;'
        #lime_survey_data_to_import = lime_survey_header
        #for token in sorted_tokens:
            #survey_friendly_name = conn.DLookup("friendly_name", "ls_sids", "ls_sid=%d" % (int(token[2])))
            #if last_ssid != token[0]:
                # new study subject ID, so write the previous one
                #ssoid = conn.DLookup("study_subject_oid", "subjects", "study_subject_id='%s'" % (last_ssid))
                # skip the start-value 
                #if last_ssid != 'x':
                    #ls_data_in_db = conn.DLookup("ls_data", "subjects", "study_subject_oid='%s'" % (ssoid))
                    #if lime_survey_data_to_import != ls_data_in_db:
                        #myImport = myDataWS.importLSData(ssoid, lime_survey_data_to_import)
                        #conn.WriteLSDataToDB(ssoid, lime_survey_data_to_import, myImport)
                        #my_report.append_to_report('wrote ls_data for subject %s 1' % (ssoid))
    
                # reset the variables
                #last_ssid = token[0]
                #lime_survey_data_to_import = lime_survey_header + survey_friendly_name + ' ' + token[3] + ' ' + token[4] + '&#10;'
            #else:
                #lime_survey_data_to_import = lime_survey_data_to_import + survey_friendly_name + ' ' +  token[3] + ' ' +  token[4] + '&#10;'
        
        # print the last one
        #ssoid = conn.DLookup("study_subject_oid", "subjects", "study_subject_id='%s'" % (last_ssid))
        #ls_data_in_db = conn.DLookup("ls_data", "subjects", "study_subject_oid='%s'" % (ssoid))
        #if lime_survey_data_to_import != ls_data_in_db:
            #myImport = myDataWS.importLSData(ssoid, lime_survey_data_to_import)
            #conn.WriteLSDataToDB(ssoid,lime_survey_data_to_import, myImport)
            #my_report.append_to_report('wrote ls_data for subject %s 2' % (ssoid))
        
