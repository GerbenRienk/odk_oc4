'''
Copied on 7 Nov 2019
from rotzak
@author: GerbenRienk
'''

from utils.dictfile import readDictFile
from utils.oc4_api import OC4Api



if __name__ == '__main__':

    # read configuration file for client id and client secret and other parameters
    config=readDictFile('odkoc4.config')
    
    # start with requesting an authentication token, which we can use for some time
    api = OC4Api(config['apiUrl'])
    aut_token = api.sessions.get_authentication_token(config['autApiUrl'], config['oc4_username'], config['oc4_password'])
    print('access token: %s\n' % aut_token)
    
    #try to post a file with participants
    add_result = api.participants.add_participant(config['studyOid'], config['siteOid'], "IMP009", aut_token)
    print('add study subject: %s\n' % add_result)
    
    event_info = {"subjectKey":"IMP008", "studyEventOID":"SE_IMPEV", "startDate":"2019-11-01", "endDate":"2019-11-01"}
    schedule_result = api.events.schedule_event(config['studyOid'], config['siteOid'], event_info, aut_token)
    print('schedule event: %s\n' % schedule_result)
    
    
    # with this token, request the participants of the study
    print('retrieving all subjects from oc4 \n')
    all_participants = api.participants.list_participants(config['studyOid'], aut_token)
    for participant in all_participants:
        print(participant['subjectKey'] + " " + participant['subjectOid'])
    
    


