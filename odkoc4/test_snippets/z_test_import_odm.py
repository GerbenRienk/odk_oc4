'''
Copied on 11 Nov 2019
from oc4_api_test
@author: GerbenRienk
'''
import time
from utils.dictfile import readDictFile
from utils.oc4_api import OC4Api

# get variables from config-file
config=readDictFile('odkoc4.config')    
# start with requesting an authentication token, which we can use for some time
api = OC4Api(config['apiUrl'])
aut_token = api.sessions.get_authentication_token(config['autApiUrl'], config['oc4_username'], config['oc4_password'])

import_result = api.clinical_data.import_odm(aut_token, 'odm_SS_T564.xml', verbose=True)
print(import_result)
