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
from utils.pg_api import ConnToOdkDB

from _operator import itemgetter

def cycle_through_syncs():
    # we start by reading the config file and preparing the connections to the databases 
    
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    # read configuration file for tables, fields and oc4 oid's
    conn_odk= ConnToOdkDB(config, verbose=False)
    selected_values = conn_odk.GetMultiAnswers('odk_am001."10103_PAGE_WELCOME_ICP_GRP_ICF_TYPE"', 'uid:d90ae4f7-e4cf-4eaa-a599-580dce714a39')
    print(selected_values)
    
    
if __name__ == '__main__':
    cycle_through_syncs()

