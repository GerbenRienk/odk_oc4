'''
To connect to postgresql database as defined in odkoc.config
Read subjects and write subjects
Created on 14 apr. 2017

@author: GerbenRienk
'''
import psycopg2
from psycopg2.extras import RealDictCursor

class ConnToOdkUtilDB(object):
    '''Class for connecting to the postgresql database as defined in odkoc.config
    Methods implemented now are read subjects and add subjects '''
    def __init__(self, config, verbose=False):
        

        'try to create the connection to use multiple times '
        conn_string = "host='" + config['db_util_host'] + "' dbname='" + config['db_util_name'] + "' user='" + config['db_util_user'] + "' password='" + config['db_util_pass'] + "' port='" + config['db_util_port'] + "'" 
        
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


    def ReadSubjectsFromDB(self):
        'method to read table subjects into a list'
        cursor = self._conn.cursor()  
        try:
            cursor.execute("""SELECT * from subjects""")
        except:
            print ("not able to execute the select")
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
        sql_statement = """INSERT INTO study_subject_oc (study_subject_oid,study_subject_id) VALUES ('%s', '%s')""" % (study_subject_oid, study_subject_id)
        
        try:
            cursor.execute(sql_statement)
        except:
            print ("AddSubjectToDB: not able to execute the insert '%s', '%s' " % (study_subject_oid, study_subject_id))
            print ("using '%s' " % (sql_statement))
        self._conn.commit()
        return None

    def CheckAndUpdate(self, study_subject_id, study_subject_oid):
        # first check if the id is in the util db
        if(self.DCount('*', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)==0):
            self.AddSubjectToDB(study_subject_oid, study_subject_id)
        
        if (self.DLookup('study_subject_oid', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)!=study_subject_oid):
            # id is ok, but oid not, so update the table
            cursor = self._conn.cursor()  
            update_statement = "update study_subject_oc set study_subject_oid='%s' where study_subject_id='%s'" % (study_subject_oid, study_subject_id)
            try:
                cursor.execute(update_statement)
            except:
                print ("not able to execute the update %s" % update_statement)
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
    
    def MarkUriComplete(self, uri, table_name = 'none'):
        '''method to call with an odk-uri as parameter
        calling it will set the status of the uri to complete in table odkoc.uri_status
        '''
        cursor = self._conn.cursor()  
        try:
            cursor.execute("insert into odkoc.uri_status (uri, last_update_status, is_complete, table_name) select '%s', now(), true, '%s'" % (uri, table_name))
        except:
            print ("MarkUriComplete: not able to execute the update")
        self._conn.commit()
        

    def UriComplete(self, uri):
        '''method to call with an odk-uri as parameter
        if uri has been processed an data have been impotred into oc
        then return true,
        otherwise return false
        '''
        if(self.DLookup('is_complete', 'odkoc.uri_status', "uri='%s'" % uri)):
            _uri_status = True
        else:
            _uri_status = False
        return _uri_status

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

        
    def ReadDataFromOdkTable(self, table_name, where_clause = 'True'):
        'method to read table subjects into a list'
        cursor = self._conn.cursor(cursor_factory=RealDictCursor)  
        sql_statement = "SELECT * from " + table_name + " where " + where_clause
        try:
            cursor.execute(sql_statement)
        except:
            print ("ReadDataFromOdkTable: not able to execute: " + sql_statement)
        results = cursor.fetchall()
        return results


if __name__ == "__main__":
    pass    