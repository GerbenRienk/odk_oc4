'''
Created on 9 apr. 2017

@author: GerbenRienk
'''

import hashlib
import zeep 
from lxml import etree
from zeep.wsse import UsernameToken
import requests

class studySubjectWS(object):
    '''
    class for the study subject webservice:
    to retrieve all study events for one Study
    '''

    def __init__(self, username, password, baseUrl):
        self._username = username
        passwordHash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        self._passwordHash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        wsUrl = baseUrl + '/ws/study/v1/studySubjectWsdl.wsdl'
        self._thisURL = wsUrl
        self._client = zeep.Client(
            wsUrl,
            strict=False,
            wsse=UsernameToken(username, password=passwordHash))
        
    def getStudySubjectEvents(self,studyIdentifier):
        """Get xml output of study subject events

        """
        with self._client.options(raw_response=True):
            response = self._client.service.listAllByStudy({
                'identifier': studyIdentifier
                })
            if response.status_code != 200:
                return None

            #the response needs cleaning up
            document = str(response.content)
            document = document[document.index('<SOAP'):]
            document = document[0:document.index('</SOAP-ENV:Envelope>') + 20]
            
            xml_output = etree.fromstring(document)
            relevant_part = xml_output.xpath('//ns4:studySubjects', namespaces={
                'ns2': 'http://openclinica.org/ws/beans', 'ns4': 'http://openclinica.org/ws/studySubject/v1'
            })
            return relevant_part

    def getListStudySubjectEvents(self,studyIdentifier):
        for all_subjects in self.getStudySubjectEvents(studyIdentifier):    
            #initialise a list to return
            all_studysubject_events = []
            for one_subject in all_subjects.xpath('//ns2:studySubject', namespaces={'ns2': 'http://openclinica.org/ws/beans'}):
                for one_subject_infoblocks in one_subject.getchildren():
                    #is this the label?
                    if one_subject_infoblocks.tag == '{http://openclinica.org/ws/beans}label':
                        studySubjectID = one_subject_infoblocks.text
                    if one_subject_infoblocks.tag == '{http://openclinica.org/ws/beans}events':
                        for all_events in one_subject_infoblocks.getchildren():
                            for one_event_info in all_events.getchildren():
                                if one_event_info.tag == '{http://openclinica.org/ws/beans}eventDefinitionOID':
                                    eventDefinitionOID = one_event_info.text
                                if one_event_info.tag == '{http://openclinica.org/ws/beans}startDate':
                                    startDate = one_event_info.text
                            
                            one_studysubject_event = studySubjectID,eventDefinitionOID,startDate
                            all_studysubject_events.append(one_studysubject_event)
                            
        return all_studysubject_events

    def getListStudySubjects(self,studyIdentifier):
        for all_subjects in self.getStudySubjectEvents(studyIdentifier):    
            #initialise a list to return
            all_studysubjects = []
            for one_subject in all_subjects.xpath('//ns2:studySubject', namespaces={'ns2': 'http://openclinica.org/ws/beans'}):
                for one_subject_infoblocks in one_subject.getchildren():
                    #is this the label?
                    if one_subject_infoblocks.tag == '{http://openclinica.org/ws/beans}label':
                        studySubjectID = one_subject_infoblocks.text
                               
                one_studysubject = studySubjectID
                all_studysubjects.append(one_studysubject)
                            
        return all_studysubjects

    def addStudySubject(self,studyIdentifier, siteIdentifier, studysubjectid):
     
        headers = {'content-type': 'text/xml'}
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://openclinica.org/ws/studySubject/v1" xmlns:bean="http://openclinica.org/ws/beans"><soapenv:Header>
 <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
 <wsse:UsernameToken wsu:Id="UsernameToken-27777511" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">"""
        body = body + '<wsse:Username>' + self._username + '</wsse:Username>'
        body = body + '<wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">' + self._passwordHash + '</wsse:Password>'
        body = body + '</wsse:UsernameToken>'
        body = body + '</wsse:Security>'
        body = body + '</soapenv:Header>'
        body = body + '<soapenv:Body>'
        body = body + '<v1:createRequest>'
        body = body + '<v1:studySubject>'
        body = body + '<bean:label>' + studysubjectid + '</bean:label>'
        body = body + '<bean:secondaryLabel></bean:secondaryLabel>'
        body = body + '<bean:enrollmentDate>1980-01-01</bean:enrollmentDate>'
        body = body + '<bean:subject>'
        body = body + '<bean:uniqueIdentifier></bean:uniqueIdentifier>'
        body = body + '<bean:gender>f</bean:gender>'
        body = body + '<bean:dateOfBirth></bean:dateOfBirth>'
        body = body + '</bean:subject>'
        body = body + '<bean:studyRef>'
        body = body + '<bean:identifier>' + studyIdentifier + '</bean:identifier>'
        body = body + '<bean:siteRef>'
        body = body + '<bean:identifier>' + siteIdentifier + '</bean:identifier>'
        body = body + '</bean:siteRef>'
        body = body + '</bean:studyRef>'
        body = body + '</v1:studySubject>'
        body = body + '</v1:createRequest>'
        body = body + '</soapenv:Body>'
        body = body + '</soapenv:Envelope>'
        
        xml_as_string = requests.post(self._thisURL,data=body,headers=headers).content.decode('utf-8')
        tree = etree.fromstring(xml_as_string)
        results = ''
        for result_tag in tree.findall('.//{http://openclinica.org/ws/studySubject/v1}result'):
            results = results + result_tag.text
        if(results == 'Fail'):
            for result_tag in tree.findall('.//{http://openclinica.org/ws/studySubject/v1}error'):
                results = 'subject ws: ' + results + ': ' + result_tag.text
        return results

class studyEventWS(object):
    '''
    class for the study event webservice:
    to add a study event
    '''

    def __init__(self, username, password, baseUrl):
        self._username = username
        passwordHash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        self._passwordHash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        wsUrl = baseUrl + '/ws/event/v1/eventWsdl.wsdl'
        self._thisURL = wsUrl
        self._client = zeep.Client(
            wsUrl,
            strict=False,
            wsse=UsernameToken(username, password=passwordHash))

    def scheduleEvent(self,studyIdentifier,studysubjectid, event_definition_oid, location, start_date):
     
        headers = {'content-type': 'text/xml'}
    
        body = ''
        body = body + '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://openclinica.org/ws/studyEventDefinition/v1" xmlns:bean="http://openclinica.org/ws/beans">'
        body = body + '  <soapenv:Header>'
        body = body + '    <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">'
        body = body + '      <wsse:UsernameToken wsu:Id="UsernameToken-27777511" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">'
        body = body + '        <wsse:Username>' + self._username + '</wsse:Username>'
        body = body + '        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">' + self._passwordHash + '</wsse:Password>'
        body = body + '      </wsse:UsernameToken>'
        body = body + '    </wsse:Security>'
        body = body + '  </soapenv:Header>'
        body = body + '  <soapenv:Body>'
        body = body + '    <v11:scheduleRequest xmlns:v11="http://openclinica.org/ws/event/v1">'
        body = body + '      <v11:event>'
        body = body + '        <bean:studySubjectRef>'
        body = body + '          <bean:label>' + studysubjectid + '</bean:label>'
        body = body + '        </bean:studySubjectRef>'
        body = body + '        <bean:studyRef>'
        body = body + '          <bean:identifier>' + studyIdentifier + '</bean:identifier>'
        body = body + '        </bean:studyRef>'
        body = body + '        <bean:eventDefinitionOID>' + event_definition_oid + '</bean:eventDefinitionOID>'
        body = body + '        <bean:location>' + location + '</bean:location>'
        body = body + '        <bean:startDate>' + start_date + '</bean:startDate>'
        body = body + '      </v11:event>'
        body = body + '    </v11:scheduleRequest>'
        body = body + '  </soapenv:Body>'
        body = body + '</soapenv:Envelope>'
        
        xml_as_string = requests.post(self._thisURL,data=body,headers=headers).content.decode('utf-8')
        tree = etree.fromstring(xml_as_string)
        results = ''
        for result_tag in tree.findall('.//{http://openclinica.org/ws/studySubject/v1}result'):
            results = results + result_tag.text
        if(results == 'Fail'):
            for result_tag in tree.findall('.//{http://openclinica.org/ws/studySubject/v1}error'):
                results = 'event ws: ' + results + ': ' + result_tag.text
        else:
            # look for this part: <studySubjectOID xmlns="http://openclinica.org/ws/event/v1">
            for result_tag in tree.findall('.//{http://openclinica.org/ws/event/v1}studySubjectOID'):
                results = result_tag.text
           
        return results

class dataWS(object):
    '''
    class for the study subject webservice:
    to import data
    '''
    def __init__(self, username, password, baseUrl):
        self._passwordHash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        self._wsUrl = baseUrl + '/ws/data/v1/dataWsdl.wsdl'
        self._username = username
        
    def importData(self,odm_data):
        
        _dataWsUrl = self._wsUrl
        
        headers = {'content-type': 'text/xml'}
        body = ''
        body = body + '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://openclinica.org/ws/data/v1" xmlns:bean="http://openclinica.org/ws/beans">'
        body = body + '  <soapenv:Header>'
        body = body + '    <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">'
        body = body + '      <wsse:UsernameToken wsu:Id="UsernameToken-27777511" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">'
        body = body + '        <wsse:Username>' + self._username + '</wsse:Username>'
        body = body + '        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">' + self._passwordHash + '</wsse:Password>'
        body = body + '      </wsse:UsernameToken>'
        body = body + '    </wsse:Security>'
        body = body + '  </soapenv:Header>'
        body = body + '  <soapenv:Body>'
        body = body + '    <v1:importRequest>'
        body = body + odm_data
        body = body + '    </v1:importRequest>'
        body = body + '  </soapenv:Body>'
        body = body + '</soapenv:Envelope>'
        
        xml_as_string = requests.post(_dataWsUrl,data=body,headers=headers).content.decode('utf-8')
        
        tree = etree.fromstring(xml_as_string)
        results = ''
        # first check if we were able to compose a valid soap request
        for soap_fault in tree.findall('.//faultstring'):
            results = results + soap_fault.text + body
        
        # now check what the web service gave as response    
        for result_tag in tree.findall('.//{http://openclinica.org/ws/data/v1}result'):
            results = results + result_tag.text
            if (result_tag.text == 'Fail'):
                for result_tag in tree.findall('.//{http://openclinica.org/ws/data/v1}error'):
                    results = 'data ws: ' + results + ': ' + result_tag.text       
        
        return results
    
if __name__ == "__main__":
    pass 