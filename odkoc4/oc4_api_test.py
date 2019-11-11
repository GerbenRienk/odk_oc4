'''
Copied on 7 Nov 2019
from rotzak
@author: GerbenRienk
'''
import time
import datetime
from utils.logmailer import MailThisLogFile
from utils.dictfile import readDictFile
from utils.oc4_api import OC4Api
#from utils.pg_api import ConnToOliDB, PGSubject
from utils.reporter import Reporter

aut_token = "x"

def cycle_through_syncs():
    # indicate that we are going to use aut_token globally
    global aut_token
    # read configuration file for client id and client secret and other parameters
    config=readDictFile('odkoc4.config')
    # start a report
    my_report = Reporter()
    
    # start with requesting an authentication token, which we can use for some time
    api = OC4Api(config['apiUrl'])
    aut_token = api.sessions.get_authentication_token(config['autApiUrl'], config['oc4_username'], config['oc4_password'])
    
    #try to post a file with participants
    #bulk_file = files = {'file': ('participants.csv', open('participants.csv', 'rb'))}
    add_result = api.participants.add_participant(config['studyOid'], config['siteOid'], "IMP008", aut_token)
    
    event_info = {"subjectKey":"IMP002", "studyEventOID":"SE_IMPEV", "startDate":"2019-11-01", "endDate":"2019-11-01"}
    schedule_result = api.events.schedule_event(config['studyOid'], config['siteOid'], event_info, aut_token)

    import_result = api.clinical_data.import_odm(aut_token)
    
    # with this token, request the participants of the study
    all_participants = api.participants.list_participants(config['studyOid'], aut_token)
    for participant in all_participants:
        print(participant['subjectKey'] + " " + participant['subjectOid'])
    
    #print('access token before loops %s' % aut_token)            
    if(aut_token is None):
        # something is wrong with either the url, the client id or the client secret 
        my_report.append_to_report('could not get a access token with given client id and secret')
    else:
        # apparenty we have a token, so let's start looping    
        start_time = datetime.datetime.now()
        my_report.append_to_report('cycle started at ' + str(start_time))
    
        # create a connection to the postgresql database
        # conn = ConnToOliDB()
        # my_report.append_to_report(conn.init_result)
        
        while True:
            # update_token(api, config)
            my_report.append_to_report('I\'m in the loop with access token %s' % aut_token)
             
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
        
        # we're finished looping, so write this in the report
        my_report.append_to_report('finished looping from %s till %s.' % (start_time, current_time))
        # close the file so we can send it

    my_report.close_file()
    # MailThisLogFile('logs/report.txt')

def update_token(api, config):
    global aut_token
    # use endpoint user to check if the access token is still valid and if not
    # then request a new one
    # let's first request the user info
    if  api.users.user(aut_token) is None:
        aut_token = api.sessions.get_authentication_token(config['client_id'], config['client_secret'])
        

    
if __name__ == '__main__':
    cycle_through_syncs()
