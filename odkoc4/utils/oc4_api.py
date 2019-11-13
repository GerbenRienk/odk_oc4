import requests
import json
from collections import OrderedDict

class OC4Api(object):

    def __init__(self, url):
        self.url = url
        self.headers = {"content-type": "application/json"}        
        self.utils = _Utils(self)
        self.sessions = _Sessions(self)
        self.users = _Users(self)
        self.participants = _Participants(self)
        self.events = _Events(self)
        self.clinical_data = _ClinicalData(self)

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
                print("req url=     %s" % url)
                print("req params=  %s" % params)
                print("req headers= %s" % headers)
                print("req data=    %s" % data)
                print("req type=    %s" % request_type)
            
            if request_type == 'post':
                #print("req type=post")
                response = requests.post(url, params=params, headers=headers, data=data, files=files)
                
            if request_type == 'get':
                #print("req type=get")
                response = requests.get(url, params=params, headers=headers, data=data)
            
            if verbose == True:
                print("req url=     %s" % response.request.url)
                print("req headers= %s" % response.request.headers)
                print("req body=    %s" % response.request.body)
                print(response.text)
                
            if response.status_code == 200:
                return_value = response.json()
            else:
                print('request to %s returned status code %i' % (url, response.status_code))
        
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

class _Users(object):

    def __init__(self, oc4_api):
        self.api = oc4_api

    def user(self, access_token, user_id=None):
        """
        Retrieve a list of users the currently authenticated user is authorized to see. 
        Default to own User.
        if a user_id is given, then only data about this user are returned
        
        :type user_id: String
        """
        my_url = self.api.url + "/api/user"
        # if a specific user id is given as parameter:
        if user_id is not None:
            my_url = my_url + "/" + user_id
            
        my_authorization = "Bearer %s" % (access_token)
        my_headers = {'Authorization': my_authorization}
        response = self.api.utils.request(request_type='get', headers=my_headers, url=my_url, data=None)
        return response

class _Participants(object):

    def __init__(self, oc4_api):
        self.api = oc4_api

    def list_participants(self, study_oid, aut_token):
        """
        List participants per study and/or per site
        /pages/auth/api/clinicaldata/studies/{studyOID}/participants
        Parameters
        :param session_key: Active LSRC2 session key
        :type session_key: String
        :param username: LimeSurvey username to list accessible surveys for.
        :type username: String
        """
        url = self.api.url + "/pages/auth/api/clinicaldata/studies/" + study_oid + "/participants"
        bearer = "bearer " + aut_token
        headers = {"Authorization": bearer}
        complete_response = self.api.utils.request(url=url, headers=headers, request_type='get')
        # pass only the main part:
        response=complete_response['studyParticipants']
        return response

    def add_participant(self, study_oid, site_oid, study_subject_id, aut_token):
        """
        Add participants to a study using a csv-file
        POST {serverName}/pages/auth/api/clinicaldata/studies/{studyOID}/sites/{siteOID}/participants
        Parameters
        :param study_oid: study_oid
        :type study_oid: String
        :param files: the csv-file-location 
        :type username: files = {'file': ('report.xls', open('report.xls', 'rb')}
        Header should contain: content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
        """
        url = self.api.url + "/pages/auth/api/clinicaldata/studies/" + study_oid + "/sites/" + site_oid + "/participants"
        params = {"register":"n"}
        bearer = "bearer " + aut_token
        headers = {"accept":"*/*","Content-Type": "application/json", "Authorization": bearer}
        
        data = json.dumps({"subjectKey" : study_subject_id})
        #submit request
        response = self.api.utils.request(url=url, params=params, headers=headers, request_type='post', data=data, verbose=False)
           
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
        response = self.api.utils.request(url=url, headers=headers, request_type='post', verbose=True, files=files)
                
        return response

class _Events(object):

    def __init__(self, oc4_api):
        self.api = oc4_api


    def schedule_event(self, study_oid, site_oid, event_info, aut_token):
        """
        Add participants to a study using a csv-file
        POST {serverName}/pages/auth/api/clinicaldata/studies/{studyOID}/sites/{siteOID}/participants
        Parameters
        :param study_oid: study_oid
        :type study_oid: String
        :param files: the csv-file-location 
        :type username: files = {'file': ('report.xls', open('report.xls', 'rb')}
        Header should contain: content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
        """
        url = self.api.url + "/pages/auth/api/clinicaldata/studies/" + study_oid + "/sites/" + site_oid + "/events"
        
        bearer = "bearer " + aut_token
        headers = {"accept":"*/*","Content-Type": "application/json", "Authorization": bearer}
        
        data = json.dumps(event_info)
        #submit request
        response = self.api.utils.request(url=url, headers=headers, request_type='post', data=data, verbose=False)
           
        return response

class _ClinicalData(object):

    def __init__(self, oc4_api):
        self.api = oc4_api

    def import_odm(self, aut_token):
        """
        Add participants to a study using a csv-file
        POST {serverName}/pages/auth/api/clinicaldata/studies/{studyOID}/sites/{siteOID}/participants
        Parameters
        :param study_oid: study_oid
        :type study_oid: String
        :param files: the csv-file-location 
        :type username: files = {'file': ('report.xls', open('report.xls', 'rb')}
        Header should contain: content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
        """
        url = self.api.url + "/pages/auth/api/clinicaldata/import"
        
        bearer = "bearer " + aut_token
        #headers = {"Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW", "Authorization": bearer}
        headers = {"accept": "*/*", "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW", "Authorization": bearer}
        
        files = {'file': open('odm_example.xml', 'rb')}
        #submit request
        response = self.api.utils.request(url=url, headers=headers, request_type='post', files=files, verbose=True)
           
        return response
