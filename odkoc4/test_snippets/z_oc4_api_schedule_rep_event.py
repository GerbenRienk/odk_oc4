'''
Test for OC4Api participants add_participant 
Uses pg_api to retrieve some valid job uuid's
'''
import json
from dictfile import readDictFile
from general_functions import is_jsonable
from oc4_api import OC4Api

if __name__ == '__main__':

    # read configuration file for client id and client secret and other parameters
    config=readDictFile('odkoc4.config')
    
    # start with requesting an authentication token, which we can use for some time
    api = OC4Api(config['apiUrl'])
    aut_token = api.sessions.get_authentication_token(config['autApiUrl'], config['oc4_username'], config['oc4_password'])
    print('access token: %s\n' % aut_token)

    with open('config/data_definition.json') as json_file:
        data_def = json.load(json_file)
        
    # try to add a subject / participant to oc4
    study_subject_id = 'AM001996767'
    site_oid ='S_99(TEST)'
    serk = '3'
    event_info = {"subjectKey":study_subject_id, "studyEventOID": "SE_PROTOCOLDEVIATIONS", "startDate":"1980-01-01", "endDate":"1980-01-01", "studyEventRepeatKey": serk}
    
    while True:
        # see if we can update the event with this serk
        update_result = api.events.update_event(data_def['studyOid'], site_oid, event_info, aut_token, verbose=True)
        # if we can, then the event exists and the status code will be 200
        if update_result.status_code == 200:
            break
        # the serk does not exist, so we schedule an extra event and loop again to check if this was enough
        schedule_result = api.events.schedule_event(data_def['studyOid'], site_oid, event_info, aut_token, verbose=True)
