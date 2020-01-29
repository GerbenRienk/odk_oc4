'''
Created on 20180818
extra support and a better name
@author: Gerben Rienk
'''

import json

with open('config/data_definition.json') as json_file:
    data_def = json.load(json_file)
    for odk_table in data_def['odk_tables']:
        print('table_name: ' + odk_table['table_name'])
        