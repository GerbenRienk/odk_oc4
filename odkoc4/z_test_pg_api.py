'''
Created on 20180818
extra support and a better name
@author: Gerben Rienk
'''

from utils.dictfile import readDictFile
from utils.pg_api import UtilDB
from utils.oc4_api import OC4Api
    
if __name__ == '__main__':
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    api = OC4Api(config['apiUrl'])
    aut_token = api.sessions.get_authentication_token(config['autApiUrl'], config['oc4_username'], config['oc4_password'])
    
    # create connections to the postgresql databases
    print('testing connection(s) to the database(s)\n')
    util = UtilDB(config, verbose=False)
    
    all_uris = util.uri.list()
    for one_uri in all_uris:
        uri = one_uri[0]
        uuid = one_uri[6].replace('job uuid: ','')
        