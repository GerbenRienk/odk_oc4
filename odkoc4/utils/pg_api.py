'''
To connect to postgresql database as defined in odkoc4.config
Read subjects and write subjects and keep administration of uri's

@author: GerbenRienk
'''
import psycopg2
import json
from psycopg2.extras import RealDictCursor
#from lib2to3.fixer_util import String

class _DNU_ConnToOdkUtilDB(object):
    '''Class for connecting to the postgresql database as defined in odkoc.config
    Methods implemented now are read subjects and add subjects '''
    def __init__(self):
        'try to create the connection to use multiple times '
        self.init_result = ''
        # get a connection, if a connect cannot be made an exception will be raised here
        

    def ReadSubjectsFromDB(self):
        'method to read table subjects into a list'
        cursor = self._conn.cursor() 
        sql_statement = "SELECT * from subjects"
        try:
            cursor.execute(sql_statement)
        except:
            print ("not able to execute the select: %s" % sql_statement)
        results = cursor.fetchall()
        return results
    
    def get_subject_oid(self, study_subject_id):
        
        _oid=self.DLookup("study_subject_oid", "study_subject_oc", "study_subject_id='%s'" % study_subject_id)  
        return _oid

    
    def AddSubjectsToDB(self, dict_of_subjects):
        """ Method to add a dictionary of subjects to the table subjects
        It is made to handle multiple inserts
        """
        cursor = self._conn.cursor()  
        try:
            cursor.executemany("""INSERT INTO odkoc.study_subject_oc (study_subject_oid,study_subject_id) VALUES (%s, %s)""", dict_of_subjects)
        except:
            print ("AddSubjectsToDB: not able to execute the insert")
        self._conn.commit()
        return None

    def AddSubjectToDB(self, study_subject_oid, study_subject_id):
        """ Method to add a dictionary of subjects to the table subjects
        It is made to handle multiple inserts
        """
        cursor = self._conn.cursor()  
        sql_statement = """INSERT INTO study_subject_oc (study_subject_oid,study_subject_id) VALUES (%s, %s)""" 
        
        try:
            cursor.execute(sql_statement, (study_subject_oid, study_subject_id))
        except:
            print ("AddSubjectToDB: not able to execute the insert '%s', '%s' " % (study_subject_oid, study_subject_id))
            print ("using '%s' " % sql_statement)
        self._conn.commit()
        return None

    def CheckAndUpdate(self, study_subject_id, study_subject_oid):
        # first check if the id is in the util db
        if(self.DCount('*', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)==0):
            self.AddSubjectToDB(study_subject_oid, study_subject_id)
        
        if (self.DLookup('study_subject_oid', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)!=study_subject_oid):
            # id is ok, but oid not, so update the table
            cursor = self._conn.cursor()  
            update_statement = "update study_subject_oc set study_subject_oid=%s where study_subject_id=%s"
            try:
                cursor.execute(update_statement, (study_subject_oid, study_subject_id))
            except:
                print ("not able to execute the update %s for %s, %s" % (update_statement, study_subject_oid, study_subject_id))
            self._conn.commit()   
            
        if(self.DCount('*', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)==0):
            cau_result = True
        else:
            cau_result = False
            
        return cau_result
    

    def DCount(self, field_name, table_name, where_clause):
        '''Method to read one field of a table with certain criteria
        If no result, then a list containing an empty string is returned
        '''
        cursor = self._conn.cursor()  
        sql_statement = "SELECT COUNT(%s) from %s where %s"
        
        try:
            cursor.execute(sql_statement, (field_name, table_name, where_clause))
        except:
            print ("not able to execute %s for %s, %s, %s" % (sql_statement, field_name, table_name, where_clause))
        results = cursor.fetchone()
        if not results:
            results = ['']
        return results[0]

    def DLookup(self, field_name, table_name, where_clause):
        '''Method to read one field of a table with certain criteria
        If no result, then a list containing an empty string is returned
        '''
        cursor = self._conn.cursor()  
        sql_statement = "SELECT " + field_name + " from " + table_name + " where " + where_clause
        
        try:
            cursor.execute(sql_statement)
        except:
            print ("not able to execute the select")
        results = cursor.fetchone()
        if not results:
            results = ['']
        return results[0]

    def AddUriToDB(self, uri):
        """ Method to add an odk-submission
        """
        cursor = self._conn.cursor()  
        sql_statement = """INSERT INTO uri_status (uri) select %s"""
        
        try:
            cursor.execute(sql_statement, (uri,))
        except (Exception, psycopg2.Error) as error :
            print ("error ", error)
            print ("AddUriToDB: not able to execute the insert %s " % (uri))
            print ("using '%s' " % (sql_statement))
        self._conn.commit()
        
        return None
    
class ConnToOdkDB(object):
    '''Class for connecting to the postgresql database as defined in odkoc.config
    Methods implemented now are read subjects and add subjects '''
    def __init__(self, config, verbose=False):
        'let us create the connection to use multiple times'
        #config=readDictFile('odkoc4.config')
        conn_string = "host='" + config['db_host'] + "' dbname='" + config['db_name'] + "' user='" + config['db_user'] + "' password='" + config['db_pass'] + "' port='" + config['db_port'] + "'"
        self.init_result = ''
        
        # get a connection, if a connect cannot be made an exception will be raised here
        try:
            self._conn = psycopg2.connect(conn_string)
            self.init_result = 'class connected '
        except (Exception, psycopg2.Error) as error :
            print ("error while connecting to postgres", error)
            self.init_result = 'attempt to connect not successful '
        
        if (verbose):
            print(conn_string)
            print(self.init_result)

        
    def ReadDataFromOdkTable(self, table_name, where_clause = 'True', order_clause=''):
        'method to read table subjects into a list'
        cursor = self._conn.cursor(cursor_factory=RealDictCursor)  
        # sql_statement = "SELECT * from " + table_name + " where " + where_clause
        sql_statement = "SELECT * from %s where %s" % (table_name, where_clause)
        if not order_clause == '':
            sql_statement = sql_statement + ' order by ' + order_clause
        # for debugging
        #print(sql_statement)    
        try:
            cursor.execute(sql_statement)
        except:
            print ("ReadDataFromOdkTable: not able to execute: " + sql_statement)
        results = cursor.fetchall()
        return results

    def list_double_entries(self, table_name):
        'method to read subjects that have been entered more than once'
        cursor = self._conn.cursor(cursor_factory=RealDictCursor)  
        
        sql_statement = 'select "STUDY_SUBJECT_ID", count("STUDY_SUBJECT_ID") from %s group by "STUDY_SUBJECT_ID" having count("STUDY_SUBJECT_ID")>1 order by "STUDY_SUBJECT_ID"' % (table_name,) 
            
        try:
            cursor.execute(sql_statement)
        except:
            print ("ReadDataFromOdkTable: not able to execute: " + sql_statement)
        results = cursor.fetchall()
        return results

    def GetMultiAnswers(self, table_name, parent_auri):
        'method to read table subjects into a list'
        cursor = self._conn.cursor(cursor_factory=RealDictCursor)  
        sql_statement = "SELECT \"VALUE\" from " + table_name + " where \"_PARENT_AURI\"='" + parent_auri + "' order by \"_ORDINAL_NUMBER\""
        try:
            cursor.execute(sql_statement)
        except:
            print ("GetMultiAnswers: not able to execute: " + sql_statement)
        selected_values = cursor.fetchall()
        all_options =''
        if len(selected_values) > 0:
            for option in selected_values:
                all_options = all_options + option['VALUE'] + ','
            #remove last comma
            all_options = all_options.rstrip(',')
        
        return all_options

class UtilDB(object):
    '''Class for connecting to the postgresql database as defined in odkoc.config
    Methods implemented now are read subjects and add subjects '''
    def __init__(self, config, verbose=False):
        self.subjects = _Subjects(self)
        self.uri = _URI(self)
        
        'try to create the connection to use multiple times '
        if(config['environment'] == 'test'):
            conn_string = "host='" + config['db_util_host'] + "' dbname='" + config['db_util_name_test'] + "' user='" + config['db_util_user'] + "' password='" + config['db_util_pass'] + "' port='" + config['db_util_port'] + "'" 
        else:
            conn_string = "host='" + config['db_util_host'] + "' dbname='" + config['db_util_name_prod'] + "' user='" + config['db_util_user'] + "' password='" + config['db_util_pass'] + "' port='" + config['db_util_port'] + "'"
        self.init_result = ''

        # get a connection, if a connect cannot be made an exception will be raised here
        try:
            self._conn = psycopg2.connect(conn_string)
            self.init_result = 'class connected '
            
        except (Exception, psycopg2.Error) as error :
            print ("error while connecting to postgres: %s " % error)
            self.init_result = 'attempt to connect not successful '
         
        if (verbose):
            print(conn_string)
            print(self.init_result)

class _Subjects(object):
    def __init__(self, util):
        self.util = util
          
    def list(self):
        'method to read table subjects into a list'
        cursor = self.util._conn.cursor()  
        try:
            sql_query = 'SELECT * FROM study_subject_oc'
            cursor.execute(sql_query)
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute %s : %s " % (sql_query, error))
        
        results = cursor.fetchall()
        return results
        
    def list_check_enrol(self):
        'method to read view no_enrol into a list'
        cursor = self.util._conn.cursor()  
        try:
            sql_query = 'SELECT * FROM no_enrol'
            cursor.execute(sql_query)
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute %s : %s " % (sql_query, error))
        
        results = cursor.fetchall()
        return results

    def get_subject_clinical_data(self, study_subject_oid):
        'method to read table subjects into a list'
        cursor = self.util._conn.cursor()  
        try:
            sql_query = "SELECT clinical_data_before_import FROM uri_status  where (not clinical_data_before_import is null) and study_subject_oid='%s'" % study_subject_oid
            cursor.execute(sql_query)
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute %s : %s " % (sql_query, error))
        
        results = cursor.fetchall()
        return results

        
    def get_oid(self, study_subject_id):
        cursor = self.util._conn.cursor()  
        sql_statement = "select study_subject_oid from study_subject_oc where study_subject_id=%s"
        
        try:
            cursor.execute(sql_statement, (study_subject_id,))
            results = cursor.fetchone()
            # return empty string if we have no records
            if results is None:
                results = ['']
                
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute %s\n error: %s " % (sql_statement, error))
            results = ['']
            
        return results[0]

    def add_subject(self, study_subject_oid, study_subject_id):
        """ Method to add a dictionary of subjects to the table subjects
        It is made to handle multiple inserts
        """
        cursor = self.util._conn.cursor()  
        sql_statement = """INSERT INTO study_subject_oc (study_subject_oid,study_subject_id) VALUES ('%s', '%s')""" % (study_subject_oid, study_subject_id)
        
        try:
            cursor.execute(sql_statement)
        except:
            print ("add_subject: not able to execute the insert '%s', '%s' " % (study_subject_oid, study_subject_id))
            print ("using '%s' " % (sql_statement))
        self.util._conn.commit()
        return None

    def check_enrol(self, study_subject_oid, verbose=False):
        # get all clinical data for this subject and iterate to find item 
        # with item oid I_CRF02_ENROL and then retrieve the value 
        # by default set result to false
        if verbose:
            print('check_enrol for %s' % study_subject_oid)
        ce_result = False 
        all_clinical_data = self.get_subject_clinical_data(study_subject_oid)
        for clinical_data in all_clinical_data:
            cd_json = json.loads(clinical_data[0])
            se_data = cd_json['ClinicalData']['SubjectData']['StudyEventData']
            #if verbose:
                #print('se_data: %s' % se_data)
            # create an empty list
            construct_se_data=[]
            if (type(se_data) is dict):
                construct_se_data.append(se_data)   
                if verbose:
                    print('se_data is a dict')        
            if (type(se_data) is list):
                construct_se_data=se_data
                if verbose:
                    print('se_data is a list')     
                                    
            for se in construct_se_data:
                if 'FormData' in se:
                    form_data = se['FormData']
                    construct_form_data=[]
                    if (type(form_data) is dict):
                        construct_form_data.append(form_data)  
                    if verbose:
                        print('form_data is a dict')     
                    if (type(form_data) is list):
                        construct_form_data=form_data
                    if verbose:
                        print('form_data is a list')     
                        
                    for one_form in construct_form_data:
                        item_group_data = one_form['ItemGroupData']
                        construct_group_data=[]
                        if (type(item_group_data) is dict):
                            construct_group_data.append(item_group_data)  
                        if (type(item_group_data) is list):
                            construct_group_data=item_group_data
                            
                        for one_group in construct_group_data:
                            item_data = one_group['ItemData']
                            if verbose:
                                print('in one_group[item_data]')    
                            construct_item_data=[]
                            if (type(item_data) is dict):
                                construct_item_data.append(item_data)  
                            if (type(item_data) is list):
                                construct_item_data=item_data
                                
                            for one_item in construct_item_data:
                                if one_item['@ItemOID'] == 'I_CRF02_ENROL':
                                    if one_item['@Value'] == '1':
                                        ce_result = True
           
        return ce_result

    def set_enrol_ok(self, study_subject_oid):
        # enrol is ok, so update the table
        cursor = self.util._conn.cursor()  
        update_statement = "update study_subject_oc set enrol_ok=True where study_subject_oid='%s'" % (study_subject_oid)
        try:
            cursor.execute(update_statement)
        except:
            print ("not able to execute the update %s" % update_statement)
        self.util._conn.commit()
        return
        
    def set_report_date(self, study_subject_oid):
        # enrol is ok, so update the table
        cursor = self.util._conn.cursor()  
        update_statement = "update study_subject_oc set report_date=Now() where study_subject_oid='%s'" % (study_subject_oid)
        try:
            cursor.execute(update_statement)
        except:
            print ("not able to execute the update %s" % update_statement)
        self.util._conn.commit()
        return

    def check_and_update(self, study_subject_id, study_subject_oid):
        # first check if the id is in the util db
        if(self.DCount('*', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)==0):
            self.add_subject(study_subject_oid, study_subject_id)
        
        if (self.DLookup('study_subject_oid', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)!=study_subject_oid):
            # id is ok, but oid not, so update the table
            cursor = self.util._conn.cursor()  
            update_statement = "update study_subject_oc set study_subject_oid=%s where study_subject_id=%s" 
            try:
                cursor.execute(update_statement, (study_subject_oid, study_subject_id))
            except:
                print ("not able to execute the update %s with %s" % update_statement)
            self.util._conn.commit()
           
        if(self.DCount('*', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id) == 0):
            cau_result = True
        else:
            cau_result = False
            
        return cau_result


        
    def DCount(self, field_name, table_name, where_clause):
        '''Method to read one field of a table with certain criteria
        If no result, then a list containing an empty string is returned
        '''
        cursor = self.util._conn.cursor()  
        sql_statement = "SELECT COUNT(%s) from %s where %s" % (field_name, table_name, where_clause)
        
        try:
            cursor.execute(sql_statement)
        except:
            print ("not able to execute %s" % sql_statement)
        results = cursor.fetchone()
        if not results:
            results = ['']
        return results[0]

    def DLookup(self, field_name, table_name, where_clause):
        '''Method to read one field of a table with certain criteria
        If no result, then a list containing an empty string is returned
        '''
        cursor = self.util._conn.cursor()  
        sql_statement = "select %s from %s where %s "
             
        try:
            cursor.execute(sql_statement % (field_name, table_name, where_clause))
            results = cursor.fetchone()
        except (Exception, psycopg2.Error) as error :
            print ("error: %s" % error)
            print ("_Subjects.DLookup not able to execute: %s" % sql_statement)
            results = ['']
            
        return results[0]

class _URI(object):
    def __init__(self, util):
        self.util = util
        
    def add(self, uri, study_subject_oid):
        """ method to add a new uri to the utility database
        after checking there's no record yet
        """
        cursor = self.util._conn.cursor()
        sql_statement = 'select count(*) from uri_status where uri=%s'
        try:
            cursor.execute(sql_statement, (uri,))
            results = cursor.fetchone()
        except:
            print ("not able to execute: %s" % sql_statement)
            results = ['']
        self.util._conn.commit()
        
        # if we have no record yet, we can create it
        if (results[0] == 0):
            sql_statement = 'insert into uri_status (uri, study_subject_oid, last_update_status) select %s, %s, Now()'            
            try:
                cursor.execute(sql_statement, (uri, study_subject_oid))
            except (Exception, psycopg2.Error) as error :
                print ("error: %s" % error)
                print ("_URI.add: %s" % uri)
                print ("using: '%s'" % (sql_statement))
                
            self.util._conn.commit()
            
        return None

    def list(self):
        'method to read all odk-submissions into a list'
        cursor = self.util._conn.cursor()  
        try:
            cursor.execute("""SELECT * from uri_status""")
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute the select: %s " % error)
        
        results = cursor.fetchall()
        return results

    def list_incomplete(self):
        'method to read table subjects into a list'
        cursor = self.util._conn.cursor()  
        try:
            cursor.execute("""SELECT * from uri_status where is_complete is not true""")
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute the select: %s " % error)
        
        results = cursor.fetchall()
        return results

    def is_complete(self, uri):
        ' checks if uri has been marked complete'
        cursor = self.util._conn.cursor()  
        sql_statement = 'select is_complete from uri_status where uri=%s'
        # by default set the result to False
        try:
            cursor.execute(sql_statement, (uri,))   
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute the select: %s " % error)
            
        results = cursor.fetchone()
        content = results[0]
        
        return content

    def force_import(self, uri):
        ' retrieves column force_import'
        cursor = self.util._conn.cursor()  
        sql_statement = 'select force_import from uri_status where uri=%s'
        try:
            cursor.execute(sql_statement, (uri,))   
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute the select: %s " % error)
            
        results = cursor.fetchone()
        content = results[0]
        
        return content

    def has_import_errors(self, uri):
        ' checks if certain words/messages are in the import log'
        cursor = self.util._conn.cursor()  
        sql_statement = 'select job_uuid_content from uri_status where uri=%s'
        try:
            cursor.execute(sql_statement, (uri,))   
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute the select: %s " % error)
        
        results = cursor.fetchone()
        content = results[0]
        # now we look for certain content, but by default we assume no errors
        errors = False
        messages = {'errorCode','Failed','(...)', 'error.jobInProgress'}
        if not content is None:
            for message in messages:
                # print('check for %s: ' % message)
                if(message in content):
                    errors = True
        return errors

    def reset_complete(self, uri):
        """ 
        method to set the field is_complete to false
        of a certain uri to the utility database
        """    
        cursor = self.util._conn.cursor()
        sql_statement = 'update uri_status set is_complete=False where uri=%s'
        try:
            cursor.execute(sql_statement, (uri,))   
        except (Exception, psycopg2.Error) as error :
            print ("error: %s" % error)
            print ("_URI.reset_complete: %s" % uri)
            print ("using: '%s'" % (sql_statement))
            
        self.util._conn.commit()
            
        return None

    def set_complete(self, uri):
        """ 
        method to set the field is_complete to true
        of a certain uri to the utility database
        """    
        cursor = self.util._conn.cursor()
        sql_statement = 'update uri_status set is_complete=True where uri=%s'
        try:
            cursor.execute(sql_statement, (uri,))   
        except (Exception, psycopg2.Error) as error :
            print ("error: %s" % error)
            print ("_URI.reset_complete: %s" % uri)
            print ("using: '%s'" % (sql_statement))
            
        self.util._conn.commit()
            
        return None

    def write_import_result(self, uri, import_job_content):
        """ 
        method to write the name plus content of an odm file
        of a certain uri to the utility database
        """    
        cursor = self.util._conn.cursor()
        sql_statement = 'update uri_status set last_update_status=Now(), job_uuid_content=%s where uri=%s'
        try:
            cursor.execute(sql_statement, (import_job_content, uri))   
        except (Exception, psycopg2.Error) as error :
            print ("error: %s" % error)
            print ("_URI.write_odm: %s" % uri)
            print ("using: '%s'" % (sql_statement))
            
        self.util._conn.commit()
            
        return None

    def write_job_id(self, uri, import_job_uuid):
        """ 
        method to write the name plus content of an odm file
        of a certain uri to the utility database
        """    
        cursor = self.util._conn.cursor()
        sql_statement = 'update uri_status set last_update_status=Now(), import_job_uuid=%s where uri=%s'
        try:
            cursor.execute(sql_statement, (import_job_uuid, uri))   
        except (Exception, psycopg2.Error) as error :
            print ("error: %s" % error)
            print ("_URI.write_odm: %s" % uri)
            print ("using: '%s'" % (sql_statement))
            
        self.util._conn.commit()
            
        return None
    
    def write_odm(self, uri, odm_file_name):
        """ 
        method to write the name plus content of an odm file
        of a certain uri to the utility database
        """
        odm_file = open('request_files/' + odm_file_name, 'r')
        content = odm_file.read()
        odm_file.close()
        
        cursor = self.util._conn.cursor()
        sql_statement = 'update uri_status set last_update_status=Now(), odm_content=%s, odm_file_name=%s where uri=%s'
        try:
            cursor.execute(sql_statement, (content, odm_file_name, uri))   
        except (Exception, psycopg2.Error) as error :
            print ("error: %s" % error)
            print ("_URI.write_odm: %s" % uri)
            print ("using: '%s'" % (sql_statement))
            
        self.util._conn.commit()
            
        return None
    
    def write_table_name(self, uri, table_name):
        """ 
        method to write the name plus content of an odm file
        of a certain uri to the utility database
        """       
        cursor = self.util._conn.cursor()
        sql_statement = 'update uri_status set last_update_status=Now(), table_name=%s where uri=%s'
        try:
            cursor.execute(sql_statement, (table_name, uri))   
        except (Exception, psycopg2.Error) as error :
            print ("error: %s" % error)
            print ("_URI.write_table_name: %s" % uri)
            print ("using: '%s'" % (sql_statement))
            
        self.util._conn.commit()
            
        return None
    
    def get_clinical_data(self, uri):
        'method to read table subjects into a list'
        cursor = self.util._conn.cursor()  
        try:
            sql_query = "SELECT clinical_data_before_import FROM uri_status  where uri='%s'" % uri
            cursor.execute(sql_query)
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute %s : %s " % (sql_query, error))
        
        results = cursor.fetchall()
        return results

    def set_clinical_data(self, uri, clinical_data):
        cursor = self.util._conn.cursor()
                
        sql_statement = "update uri_status set clinical_data_before_import=%s where uri=%s"          
        try:
            cursor.execute(sql_statement, (clinical_data, uri))
        except (Exception, psycopg2.Error) as error :
            print ("error: %s" % error)
            print ("using: '%s'" % (sql_statement))
            
        self.util._conn.commit()
            
        return None

    def has_data_in_itemgroup(self, uri, study_event_oid, form_oid, item_group_oid, serk=0, verbose=False):
        'check for data in a specific item group '
        cursor = self.util._conn.cursor()
        try:
            sql_query = "SELECT clinical_data_before_import FROM uri_status where uri=%s"
            cursor.execute(sql_query, (uri,))
        except (Exception, psycopg2.Error) as error :
            print ("has_data_in_itemgroup: not able to execute %s for %s: %s" % (sql_query, uri, error))
            
        results = cursor.fetchall()
        cd_json = json.loads(results[0][0])
        se_data = cd_json['ClinicalData']['SubjectData']['StudyEventData']
               
        # by default we set item_group_data_exist to False
        item_group_data_exist = False
        # a subject can have one event or more
        if (verbose):
            print('looking for: %s-%s-%s-%s' % (study_event_oid, str(serk), form_oid, item_group_oid))
            print('study event data: %s' % se_data)
        
        # FormData may be in se_data, but maybe not
        forms_exist = False
        if (type(se_data) is dict):
            # study event can be repeating or not, i.e. have a serk or not
            if serk == 0:
                if (verbose):
                    print('one event, no serk')
                if (se_data['@StudyEventOID'] == study_event_oid):
                    if 'FormData' in se_data:
                        forms_exist = True
                        form_data = se_data['FormData']
            else:
                if (verbose):
                    print('one event with serk')
                if (se_data['@StudyEventOID'] == study_event_oid) and (se_data['@StudyEventRepeatKey'] == str(serk)):
                    if 'FormData' in se_data:
                        forms_exist = True
                        form_data = se_data['FormData']
                
        if (type(se_data) is list):
            if serk == 0:
                if (verbose):
                    print('more than one event, no serk')
                for one_event in se_data:
                    if (one_event['@StudyEventOID'] == study_event_oid):
                        if 'FormData' in one_event:
                            forms_exist = True
                            form_data = one_event['FormData']
            else:
                if (verbose):
                    print('more than one event with serk')
                for one_event in se_data:
                    if (one_event['@StudyEventOID'] == study_event_oid) and (one_event['@StudyEventRepeatKey'] == str(serk)):
                        if ('FormData' in one_event):
                            forms_exist = True
                            form_data = one_event['FormData']
                
        # only continue if forms exist
        if forms_exist: 
            if (verbose):
                print('form data: %s' % form_data)
            # first we must check if we have one form in the event, or more
            # set a flag to indicate that we have any groups at all to False
            groups_exist = False
            if (type(form_data) is dict):
                if (form_data['@FormOID'] == form_oid):
                    item_group_data = form_data['ItemGroupData']
                    groups_exist = True
                    
            if (type(form_data) is list):
                for one_form in form_data:
                    if (one_form['@FormOID'] == form_oid):
                        item_group_data = one_form['ItemGroupData']
                        groups_exist = True
            
            if (groups_exist):            
                # now we must check if this form has one item group or more
                if (type(item_group_data) is dict):
                    if (item_group_data['@ItemGroupOID'] == item_group_oid):
                        item_group_data_exist = True
                        
                if (type(item_group_data) is list):
                    for one_item_group in item_group_data:
                        if (one_item_group['@ItemGroupOID'] == item_group_oid):
                            item_group_data_exist = True
                    
        return item_group_data_exist
        
    
if __name__ == "__main__":
    pass    