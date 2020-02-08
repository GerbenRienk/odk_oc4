'''
Copied on 7 Nov 2019
from rotzak
@author: GerbenRienk
'''

from utils.dictfile import readDictFile
from utils.oc4_api import OC4Api
from utils.pg_api import UtilDB

if __name__ == '__main__':

    # read configuration file for client id and client secret and other parameters
    config=readDictFile('odkoc4.config')
    util = UtilDB(config, verbose=False)
    # start with requesting an authentication token, which we can use for some time
    api = OC4Api(config['apiUrl'])
    aut_token = api.sessions.get_authentication_token(config['autApiUrl'], config['oc4_username'], config['oc4_password'])
    print('access token: %s\n' % aut_token)
    
    # with this token, request the participants of the study
    print('try to retrieve all uri \n')
    all_uris = util.uri.list()
    for uri in all_uris:
        print(uri[6])
        job_result = api.jobs.download_file(aut_token, uri[6], verbose=True)
    


