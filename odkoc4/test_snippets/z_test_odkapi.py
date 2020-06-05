'''
Created on 20200406
based on 
https://forum.opendatakit.org/t/python-module-for-accessing-odk-aggregate/9301/2
and
https://github.com/Ghini

The purpose of this script is to iterate trough odk-tables for attached files and extract these on the file-system
so that they are browsable

@author: Gerben Rienk
'''

import requests
import xml.etree.ElementTree as ET
import re

import datetime
import json
import time
import os

from utils.dictfile import readDictFile
from utils.general_functions import is_jsonable
from utils.logmailer import Mailer
from utils.odk_api import OdkApi
from utils.pg_api import UtilDB, ConnToOdkDB
from utils.reporter import Reporter

from _operator import itemgetter

def check_it():
    # set these variables
    form_id = '90001'
    group_name = 'CRF99-ImageTest' 
    my_report = Reporter()
    config=readDictFile('odkoc4.config')
    with open('config/data_definition.json') as json_file:
        data_def = json.load(json_file)
    
    # create connections to the postgresql databases
    my_report.append_to_report("preparing connections")
    util = UtilDB(config, verbose=False)
    my_report.append_to_report('try to connect to util database, result: %s ' % util.init_result)
    conn_odk= ConnToOdkDB(config, verbose=False)
    my_report.append_to_report('try to connect to odk database, result: %s \n' % conn_odk.init_result)
    # start an instance with the configuration from the config file
    odkapi = OdkApi(config)
    submissions = odkapi.submissions.list(form_id, verbose=False)
    if submissions.status_code!=200:
        my_report.append_to_report('call %s resulted in status code %s' % (submissions.request.url, submissions.status_code))
    else:
        # we have the submissions
        # print('the works: \n %s \n' % submissions.text)
        root = ET.fromstring(submissions.text)
        
        for idlist in root.iter('{http://opendatakit.org/submissions}idList'):
            uuid_list = []
            for id in idlist.iter('{http://opendatakit.org/submissions}id'):
                uuid_list.append(id.text)
        
        # now we have the uuid's so let's get the data
        for uuid in uuid_list:
            print('\na new uuid: %s' % uuid)
            submission_data = odkapi.submissions.get_data(form_id, group_name, uuid, verbose=False)
            data_xml = ET.fromstring(submission_data.text)
            for data_items in data_xml.iter('{http://opendatakit.org/submissions}data'):
                for child in data_items[0]:
                    print('child: ', child.tag, child.text)
            
            print('---')
            for media_file in data_xml.iter('{http://opendatakit.org/submissions}mediaFile'):
                print('media_file: ', media_file.tag, media_file.text)
                for child in media_file:
                    print('child: ', child.tag, child.text)

    return

def get_submissions(user, pw, host, form_id, to_skip=[]):
    
    # print(result.text)
    root = ET.fromstring(result.text)
    idlist = root[0]
    result = []
    print('before uuid')
    for uuid in [i.text for i in idlist]:
        if uuid in to_skip:
            continue
        try:
            print('in try, %s' % uuid)
            reply = requests.get((base_format % {'form_id': form_id,
                                                 'api': 'downloadSubmission',
                                                 'host': host} +
                                  submission_format % {'group_name': 'CRF99-ImageTest',
                                                       'uuid': uuid}), auth=auth)
        except requests.exceptions.ConnectionError as e:
            continue
        
        print(reply.text)
        root = ET.fromstring(reply.text)
        data = root[0]  # media may follow
        form = data[0]
        item = dict([(re.sub(r'{.*}(.*)', r'\1', i.tag), i.text) for i in form])
        item['meta:uuid'] = uuid
        result.append(item)
        for key in list(item.keys()):
            if not key.endswith('_repeat'):
                continue
            del item[key]
            prefix = key[:-7]
            item[prefix] = [i[0].text for i in form if i.tag.endswith(key)]
        item['media'] = {}
        for i, media_element in enumerate(root[1:]):
            filename, hash, url = media_element
            item['media'][filename.text] = (url.text, hash.text)
    return result


def get_image(user, pw, url, path):
    auth = HTTPDigestAuth(user, pw)
    pic = requests.get(url, stream=True, auth=auth)
    if pic.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in pic.iter_content(1024):
                f.write(chunk)
                
                
if __name__ == '__main__':
    check_it()