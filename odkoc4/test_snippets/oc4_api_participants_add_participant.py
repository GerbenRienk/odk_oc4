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
    study_subject_id = 'T20200208_A'
    add_result = api.participants.add_participant(data_def['studyOid'], data_def['siteOid'], study_subject_id, aut_token, verbose=True)
    print(add_result)
    if(is_jsonable(add_result)):
        new_participant = json.loads(add_result)
        print(new_participant['subjectKey'])
    else:
        print('result was not jsonable: %s' % add_result)