import requests
import json

class OdkApi(object):

    def __init__(self, config):
        self.url = config['odk_api_url']
        self.user = config['odk_api_username']
        self.password = config['odk_api_password']
        self.headers = {"content-type": "application/json"}        
        self.jobs = _Jobs(self)
        self.utils = _Utils(self)
        self.submissions = _Submissions(self)
        self.events = _Events(self)
        self.clinical_data = _ClinicalData(self)
        self.odm_parser = _ODMParser

class _Utils(object):

    def __init__(self, odk_api):
        self.api = odk_api

    def request(self, data=None, request_type=None, url=None, headers=None, params=None, files=None, verbose=False):
        """
        Return the result of an api call, or None.
        """
        auth = requests.auth.HTTPDigestAuth(self.api.user, self.api.password)
        if url is None:
            url = self.api.url
        if headers is None:
            headers = self.api.headers
        return_value = None
        try:
            if verbose == True:
                print("p url=     %s   " % url)
                #print("p params=  %s   " % params)
                #print("p headers= %s   " % headers)
                #print("p data=    %s   " % data)
                print("p user=    %s   " % self.api.user)
                print("p type=    %s \n" % request_type)
            
            if request_type == 'post':
                response = requests.post(url, params=params, headers=headers, data=data, files=files, auth=auth)
                
            if request_type == 'get':
                response = requests.get(url, params=params, headers=headers, data=data, auth=auth)
            
            if request_type == 'put':
                response = requests.put(url, params=params, headers=headers, data=data)
            
            if request_type == 'delete':
                response = requests.delete(url, params=params, headers=headers, data=data)
            
            if verbose == True:
                #print("req url         = %s   " % response.request.url)
                #print("req headers     = %s   " % response.request.headers)
                #print("req body        = %s   " % response.request.body)
                print("resp status code= %s   " % response.status_code)
                print("resp text       = %s \n" % response.text)
            
            return_value = response 
                       
        except requests.ConnectionError as pe:
            # TODO: some handling here, for now just print pe
            print('when a request to the odk api was made, the following error was raised %s' % (pe))
            return_value = None
        
        return return_value
    
class _Submissions(object):

    def __init__(self, odk_api):
        self.api = odk_api

    def list(self, form_id, verbose=False):
        """
        list submissions per form-id
        """
        url = self.api.url + "/view/submissionList?formId=%s" % form_id
        response = self.api.utils.request(url=url, request_type='get', verbose=verbose)
        
        return response

    def get_data(self, form_id, group_name, uuid, verbose=False):
        """
        retrieve data of a particular submission per form-id
        reply = requests.get((base_format % {'form_id': form_id,
                                                 'api': 'downloadSubmission',
                                                 'host': host} +
                                  submission_format % {'group_name': 'CRF99-ImageTest',
                                                       'uuid': uuid}), auth=auth)
        base_format = 'https://%(host)s/view/%(api)s?formId=%(form_id)s'
        submission_format = '[@version=null and @uiVersion=null]/%(group_name)s[@key=%(uuid)s]'
        """
        url = self.api.url + "/view/downloadSubmission?formId=%s[@version=null and @uiVersion=null]/%s[@key=%s]" % (form_id, group_name, uuid)
        response = self.api.utils.request(url=url, request_type='get', verbose=verbose)
        
        return response

    def add_participant(self, study_oid, site_oid, study_subject_id, aut_token, verbose=False):
        """
        Add a participants to a study / site
        POST {serverName}/pages/auth/api/clinicaldata/studies/{studyOID}/sites/{siteOID}/participants
        Parameters
        :param study_oid: study_oid
        :type study_oid: String
        """
        url = self.api.url + "/pages/auth/api/clinicaldata/studies/" + study_oid + "/sites/" + site_oid + "/participants"
        params = {"register":"n"}
        bearer = "bearer " + aut_token
        headers = {"accept":"*/*","Content-Type": "application/json", "Authorization": bearer}
        
        data = json.dumps({"subjectKey" : study_subject_id})
        #submit request
        response = self.api.utils.request_2(url=url, params=params, headers=headers, request_type='post', data=data, verbose=verbose)
           
        return response

    def bulk_add_participants(self, study_oid, site_oid, files, aut_token):
        """
        Add participants to a study using a csv-file
        POST {serverName}/pages/auth/api/clinicaldata/studies/{studyOID}/sites/{siteOID}/participants/bulk
        Parameters
        :param study_oid: study_oid
        :type study_oid: String
        :param files: the csv-file-location 
        :type username: files = {'file': ('report.xls', open('report.xls', 'rb')}
        Header should contain: content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
        """
        url = self.api.url + "/pages/auth/api/clinicaldata/studies/" + study_oid + "/sites/" + site_oid + "/participants/bulk?register=n"
        bearer = "bearer " + aut_token
        headers = {"content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW", "Authorization": bearer}
        response = self.api.utils.request_2(url=url, headers=headers, request_type='post', verbose=True, files=files)
                
        return response

class _Events(object):

    def __init__(self, oc4_api):
        self.api = oc4_api

    def schedule_event(self, study_oid, site_oid, event_info, aut_token, verbose=False):
        """
        Schedule one events
        """
        url = self.api.url + "/pages/auth/api/clinicaldata/studies/" + study_oid + "/sites/" + site_oid + "/events"
        
        bearer = "bearer " + aut_token
        headers = {"accept":"*/*","Content-Type": "application/json", "Authorization": bearer}
        
        data = json.dumps(event_info)
        #submit the request
        result = self.api.utils.request(url=url, headers=headers, request_type='post', data=data, verbose=verbose)
        # hopefully the request resulted in status code 200, which is fine for us, but also 400 is good
        if(result.status_code == 200 or result.status_code == 400):
            result = None
        # if this is not the case something went wrong, so we just return whatever the response was
         
        return result

    def update_event(self, study_oid, site_oid, event_info, aut_token, verbose=False):
        """
        Change an event
        """
        url = self.api.url + "/pages/auth/api/clinicaldata/studies/" + study_oid + "/sites/" + site_oid + "/events"
        
        bearer = "bearer " + aut_token
        headers = {"accept":"*/*","Content-Type": "application/json", "Authorization": bearer}
        
        data = json.dumps(event_info)
        #submit the request
        result = self.api.utils.request(url=url, headers=headers, request_type='put', data=data, verbose=verbose)
        # hopefully the request resulted in status code 200, which is fine for us, but also 400 is good
        #if(result.status_code == 200 or result.status_code == 200):
            #result = None
        # if this is not the case something went wrong, so we just return whatever the response was
         
        return result

    def check_events(self, study_oid, aut_token, verbose=False):
        """
        It's a mystery what this end-point does, but it's in the swagger, so we leave it for now
        """
        url = self.api.url + "/pages/auth/api/%s/events/check" % study_oid 
        bearer = "bearer " + aut_token
        headers = {"accept":"*/*","Content-Type": "application/json", "Authorization": bearer}
        #submit the request
        result = self.api.utils.request(url=url, headers=headers, request_type='get', verbose=verbose)
        return result

class _ClinicalData(object):

    def __init__(self, oc4_api):
        self.api = oc4_api

    def get_clinical_data(self, aut_token, study_oid, study_subject_oid, verbose=False):
        """
        Get the clinical data from the c4 api
        
        """
        _url = self.api.url + "/pages/auth/api/clinicaldata/" + study_oid + "/" + study_subject_oid + "/*/*?includeMetadata=n"
        _bearer = "bearer " + aut_token
        _headers = {"accept":"*/*","Content-Type": "application/json", "Authorization": _bearer}

        #submit request
        response = self.api.utils.request(url=_url, headers=_headers, request_type='get', verbose=verbose)
           
        return response

    def import_odm(self, aut_token, file_name, verbose=False):
        """
        
        Header should contain: content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
        """
        _url = self.api.url + "/pages/auth/api/clinicaldata/import"
        
        _bearer = "bearer " + aut_token
        _headers = {"accept": "*/*", "Authorization": _bearer}
        _files = {'file': (file_name, open('request_files/%s' % file_name, 'rb'), 'text/xml')}

        #submit request
        response = self.api.utils.request_2(url=_url, headers=_headers, request_type='post', files=_files, verbose=verbose)
           
        return response

class _Jobs(object):

    def __init__(self, oc4_api):
        self.api = oc4_api

    def delete_file(self, aut_token, job_uuid, verbose=False):
        """
        delete the log file of a job from the server
        """
        # remove the prefix:
        _job_uuid = job_uuid.replace('job uuid: ','')
        _url = self.api.url + "/pages/auth/api/jobs/%s" % _job_uuid
        _bearer = "bearer " + aut_token
        _headers = {"accept": "*/*", "Authorization": _bearer}
        response = self.api.utils.request_2(url=_url, headers=_headers, request_type='delete', verbose=verbose)
           
        return response

    def download_file(self, aut_token, job_uuid, verbose=False):
        """
        """
        # remove the prefix:
        _job_uuid = job_uuid.replace('job uuid: ','')
        _url = self.api.url + "/pages/auth/api/jobs/%s/downloadFile" % _job_uuid
        _bearer = "bearer " + aut_token
        _headers = {"accept": "*/*", "Authorization": _bearer}
        response = self.api.utils.request_2(url=_url, headers=_headers, request_type='get', verbose=verbose)
           
        return response

class _ODMParser(object):
    
    '''
    class to creates the odm file
    to which lines can be added reporting the activities of oli,
    so it can be sent at the end of the day
    '''

    def __init__(self, file_name, study_oid, subject_oid, event_oid, form_data, serk=0, verbose=False):
        '''
        Constructor
        '''
        if verbose:
            print('filename   : %s' % file_name)
            print('study oid  : %s' % study_oid)
            print('subject oid: %s' % subject_oid)
            print('event oid  : %s' % event_oid)
            print('form data  : %s' % form_data)
            print('serk       : %s' % serk)
            
            
        self._file = open('request_files/%s' % file_name,'w') 
        self._file.write('<ODM>\n')
        self._file.write('\t<ClinicalData StudyOID="%s">\n' % study_oid)
        self._file.write('\t\t<SubjectData SubjectKey="%s">\n' % subject_oid)
        if serk==0:
            self._file.write('\t\t\t<StudyEventData StudyEventOID="%s">\n' % event_oid)
        else:
            self._file.write('\t\t\t<StudyEventData StudyEventOID="%s" StudyEventRepeatKey="%s">\n' % (event_oid, serk))
        # TODO: add layout id and form status
        if form_data['Status'] == 'data entry started':
            self._file.write('\t\t\t\t<FormData FormOID="%s" OpenClinica:FormName="this_is_a_bug" OpenClinica:FormLayoutOID="%s" OpenClinica:Status="%s">\n' % (form_data['FormOID'], form_data['FormLayoutOID'], form_data['Status']))
        else:
            self._file.write('\t\t\t\t<FormData FormOID="%s" OpenClinica:FormLayoutOID="%s" OpenClinica:Status="%s">\n' % (form_data['FormOID'], form_data['FormLayoutOID'], form_data['Status']))  

    def group_open(self, item_group_oid, igrk=''):
        # ItemGroupRepeatKey="2"
        if igrk=='':
            self._file.write('\t\t\t\t\t<ItemGroupData ItemGroupOID="%s">\n' % item_group_oid)
        else:
            self._file.write('\t\t\t\t\t<ItemGroupData ItemGroupOID="%s" ItemGroupRepeatKey="%s">\n' % (item_group_oid, igrk))
        
    def add_item(self, item_oid, item_value, item_type=""):
        _final_value = item_value
        if(item_type == 'date'):
            # date can be a date-time or None
            if(not item_value is None):
                _final_value = item_value.strftime('%Y-%m-%d')
            else:
                _final_value = ''
        if(item_type == 'integer'):
            # integer can be an integer or None
            if(not item_value is None):
                _final_value = item_value
            else:
                _final_value = ''

        if(item_type == 'real'):
            # real can be a real or None
            if(not item_value is None):
                _final_value = float(item_value)
            else:
                _final_value = ''

        if(item_type == 'string'):
            # string can be a string or None
            if(not item_value is None):
                _final_value = item_value
            else:
                _final_value = ''
            
        odm_line = '\t\t\t\t\t\t'
        odm_line = odm_line + '<ItemData ItemOID="%s" Value="%s" />' % (item_oid, _final_value)
        odm_line = odm_line + '\n'
        self._file.write(odm_line)
        return None
    
    def add_multi_item(self, item_oid, selected_values):
        
            
        odm_line = '\t\t\t\t\t\t'
        odm_line = odm_line + '<ItemData ItemOID="%s" Value="%s" />' % (item_oid, selected_values)
        odm_line = odm_line + '\n'
        self._file.write(odm_line)
        return None
    
    def group_close(self):
        self._file.write('\t\t\t\t\t</ItemGroupData>\n')

    def close_file(self):
        self._file.write('\t\t\t\t</FormData>\n')
        self._file.write('\t\t\t</StudyEventData>\n')
        self._file.write('\t\t</SubjectData>\n')
        self._file.write('\t</ClinicalData>\n')
        self._file.write('</ODM>\n')
        self._file.close()
        return None
