import requests
import json
from collections import OrderedDict

class OC4Api(object):

    def __init__(self, url):
        self.url = url
        self.headers = {"content-type": "application/json"}        
        self.jobs = _Jobs(self)
        self.utils = _Utils(self)
        self.sessions = _Sessions(self)
        self.participants = _Participants(self)
        self.events = _Events(self)
        self.clinical_data = _ClinicalData(self)
        self.odm_parser = _ODMParser

class _Utils(object):

    def __init__(self, oc4_api):
        self.api = oc4_api

    def request(self, data=None, request_type=None, url=None, headers=None, params=None, files=None, verbose=False):
        """
        Return the result of an API call, or None.

        Exceptions are logged rather than raised.

        Parameters
        :param data: Method name and parameters to send to the API.
        :type data: String
        :param url: Location of the endpoint.
        :type url: String
        :param headers: HTTP headers to add to the request.
        :type headers: Dict
        :param request_type: either post or get
        Return
        :return: Dictionary containing result of API call, or None.
        """
        if url is None:
            url = self.api.url
        if headers is None:
            headers = self.api.headers
        return_value = None
        try:
            if verbose == True:
                print("p url=     %s   " % url)
                print("p params=  %s   " % params)
                print("p headers= %s   " % headers)
                print("p data=    %s   " % data)
                print("p type=    %s \n" % request_type)
            
            if request_type == 'post':
                response = requests.post(url, params=params, headers=headers, data=data, files=files)
                
            if request_type == 'get':
                response = requests.get(url, params=params, headers=headers, data=data)
            
            if request_type == 'delete':
                response = requests.delete(url, params=params, headers=headers, data=data)
            
            if verbose == True:
                print("req url         = %s   " % response.request.url)
                print("req headers     = %s   " % response.request.headers)
                print("req body        = %s   " % response.request.body)
                print("resp status code= %s   " % response.status_code)
                print("resp text       = %s \n" % response.text)
            
            return_value = response 
                       
        except requests.ConnectionError as pe:
            # TODO: some handling here, for now just print pe
            print('when a request to the oc4 api was made, the following error was raised %s' % (pe))
            return_value = None
        
        return return_value
    
    def request_2(self, data=None, request_type=None, url=None, headers=None, params=None, files=None, verbose=False):
        """
        Return the result of an API call, or None.

        Exceptions are logged rather than raised.

        Parameters
        :param data: Method name and parameters to send to the API.
        :type data: String
        :param url: Location of the endpoint.
        :type url: String
        :param headers: HTTP headers to add to the request.
        :type headers: Dict
        :param request_type: either post or get
        Return
        :return: Dictionary containing result of API call, or None.
        """
        if url is None:
            url = self.api.url
        if headers is None:
            headers = self.api.headers
        return_value = None
        try:
            if verbose == True:
                print("req url=     %s   " % url)
                print("req params=  %s   " % params)
                print("req headers= %s   " % headers)
                print("req data=    %s   " % data)
                print("req type=    %s \n" % request_type)
            
            if request_type == 'post':
                response = requests.post(url, params=params, headers=headers, data=data, files=files)
                
            if request_type == 'get':
                response = requests.get(url, params=params, headers=headers, data=data)
            
            if request_type == 'delete':
                response = requests.delete(url, params=params, headers=headers, data=data)
            
            if verbose == True:
                print("req url         = %s   " % response.request.url)
                print("req headers     = %s   " % response.request.headers)
                print("req body        = %s   " % response.request.body)
                print("resp status code= %s   " % response.status_code)
                print("resp text       = %s \n" % response.text)
                
            if response.status_code == 200:
                # check if the response is json, if not return the response
                if(self.is_jsonable(response)):
                    if verbose == True:
                        print("response is jsonable")
                    return_value = response.json()
                else:
                    if verbose == True:
                        print("response is not jsonable, returning %s: " % response.text)
                    return_value = response.text
            else:
                print('request to %s returned status code %i\n' % (url, response.status_code))
        
        except requests.ConnectionError as pe:
            # TODO: some handling here, for now just print pe
            print('when a request to the oc4 api was made, the following error was raised %s' % (pe))
            return_value = None
        
        return return_value

    def aut_request(self, data=None, url=None):
        """
        Return the a huge token as text
        """
        url = url + "/user-service/api/oauth/token"
        headers = self.api.headers
        return_value = None
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                return_value = response.text
            else:
                print('authentication request to %s returned status code %i' % (url, response.status_code))
        except requests.ConnectionError as pe:
            # TODO: some handling here, for now just print pe
            print('when an authentication request to the oc4 api was made, the following error was raised %s' % (pe))
            return_value = None
        
        return return_value

    def is_jsonable(self, x):
        try:
            json.dumps(x)
            return True
        except:
            return False
        
    @staticmethod
    def prepare_params(method, params):
        """
        Prepare remote procedure call parameter dictionary.

        Important! Despite being provided as key-value, the API treats all
        parameters as positional. OrderedDict should be used to ensure this,
        otherwise some calls may randomly fail.

        Parameters
        :param method: Name of API method to call.
        :type method: String
        :param params: Parameters to the specified API call.
        :type params: OrderedDict

        Return
        :return: JSON encoded string with method and parameters.
        """
        data = OrderedDict([
            ('method', method),
            ('params', params),
            ('id', 1)
        ])
        data_json = json.dumps(data)
        return data_json

class _Sessions(object):

    def __init__(self, oc4_api):
        self.api = oc4_api

    def get_authentication_token(self, url, username, password):
        """
        Get an access token for all subsequent API calls.

        Parameters
        :param username as defined in OpenClinica
        :type  username: String
        :param password
        :type  password: String
        
        """
        token_data = '{"username":"%s" , "password":"%s"}' % (username, password)
        response = self.api.utils.aut_request(data=token_data, url=url)
        return response


class _Participants(object):

    def __init__(self, oc4_api):
        self.api = oc4_api

    def list_participants(self, study_oid, aut_token, verbose=False):
        """
        List participants per study and/or per site
        /pages/auth/api/clinicaldata/studies/{studyOID}/participants
        Parameters
        :param study_oid: study_oid
        :type session_key: String
        :param aut_token: aut_token
        :type username: String
        """
        url = self.api.url + "/pages/auth/api/clinicaldata/studies/" + study_oid + "/participants"
        bearer = "bearer " + aut_token
        headers = {"Authorization": bearer}
        complete_response = self.api.utils.request_2(url=url, headers=headers, request_type='get', verbose=verbose)
        # pass only the main part: 
        response=json.loads(complete_response)
        return response['studyParticipants']

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
        if(result.status_code == 200 or result.status_code == 200):
            result = None
        # if this is not the case something went wrong, so we just return whatever the response was
         
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

    def __init__(self, file_name, study_oid, subject_oid, event_oid, form_data):
        '''
        Constructor
        '''
        self._file = open('request_files/%s' % file_name,'w') 
        self._file.write('<ODM>\n')
        self._file.write('\t<ClinicalData StudyOID="%s">\n' % study_oid)
        self._file.write('\t\t<SubjectData SubjectKey="%s">\n' % subject_oid)
        self._file.write('\t\t\t<StudyEventData StudyEventOID="%s">\n' % event_oid)
        # TODO: add layout id and form status
        self._file.write('\t\t\t\t<FormData FormOID="%s" OpenClinica:FormName="ImpTest" OpenClinica:FormLayoutOID="2" OpenClinica:Status="data entry started">\n' % form_data['FormOID'])
        

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
            if(item_value):
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
                _final_value = item_value
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
