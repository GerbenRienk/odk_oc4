'''
To connect to postgresql database as defined in odkoc4.config
Read subjects and write subjects and keep administration of uri's

@author: GerbenRienk
'''
import psycopg2
from psycopg2.extras import RealDictCursor

class _DNU_ConnToOdkUtilDB(object):
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

    def AddUriToDB(self, uri):
        """ Method to add a dictionary of subjects to the table subjects
        It is made to handle multiple inserts
        """
        cursor = self._conn.cursor()  
        sql_statement = """INSERT INTO uri_status (uri) select '%s'""" % (uri)
        
        try:
            cursor.execute(sql_statement)
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

class UtilDB(object):
    '''Class for connecting to the postgresql database as defined in odkoc.config
    Methods implemented now are read subjects and add subjects '''
    def __init__(self, config, verbose=False):
        self.subjects = _Subjects(self)
        self.uri = _URI(self)
        
        'try to create the connection to use multiple times '
        conn_string = "host='" + config['db_util_host'] + "' dbname='" + config['db_util_name'] + "' user='" + config['db_util_user'] + "' password='" + config['db_util_pass'] + "' port='" + config['db_util_port'] + "'" 
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
        
        self._tst = self.init_result

class _Subjects(object):
    def __init__(self, util):
        self.util = util
           
    def list(self):
        'method to read table subjects into a list'
        cursor = self.util._conn.cursor()  
        try:
            cursor.execute("""SELECT * from study_subject_oc""")
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute the select: %s " % error)
        
        results = cursor.fetchall()
        return results
        
    def get_oid(self, study_subject_id):
        
        _oid=self.DLookup("study_subject_oid", "study_subject_oc", "study_subject_id='%s'" % study_subject_id)  
        return _oid

    
    def _AddSubjectsToDB(self, dict_of_subjects):
        """ Method to add a dictionary of subjects to the table subjects
        It is made to handle multiple inserts
        """
        cursor = self.util._conn.cursor()  
        try:
            cursor.executemany("""INSERT INTO odkoc.study_subject_oc (study_subject_oid,study_subject_id) VALUES (%s, %s)""", dict_of_subjects)
        except:
            print ("AddSubjectsToDB: not able to execute the insert")
        self.util._conn.commit()
        return None

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

    def check_and_update(self, study_subject_id, study_subject_oid):
        # first check if the id is in the util db
        if(self.DCount('*', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)==0):
            self.AddSubjectToDB(study_subject_oid, study_subject_id)
        
        if (self.DLookup('study_subject_oid', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)!=study_subject_oid):
            # id is ok, but oid not, so update the table
            cursor = self.util._conn.cursor()  
            update_statement = "update study_subject_oc set study_subject_oid='%s' where study_subject_id='%s'" % (study_subject_oid, study_subject_id)
            try:
                cursor.execute(update_statement)
            except:
                print ("not able to execute the update %s" % update_statement)
            self.util._conn.commit()
        
            
        if(self.DCount('*', 'study_subject_oc', "study_subject_id='%s'" % study_subject_id)==0):
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
        sql_statement = "SELECT " + field_name + " from " + table_name + " where " + where_clause
        
        try:
            cursor.execute(sql_statement)
        except:
            print ("not able to execute the select")
        results = cursor.fetchone()
        if not results:
            results = ['']
        return results[0]

class _URI(object):
    def __init__(self, util):
        self.util = util
        
    def add(self, uri):
        """ Method to add a dictionary of subjects to the table subjects
        It is made to handle multiple inserts
        """
        cursor = self.util._conn.cursor()  
        sql_statement = """INSERT INTO uri_status (uri, last_update_status) select '%s', Now()""" % (uri)
        
        try:
            cursor.execute(sql_statement)
        except (Exception, psycopg2.Error) as error :
            print ("error ", error)
            print ("AddUriToDB: not able to execute the insert %s " % (uri))
            print ("using '%s' " % (sql_statement))
        self.util._conn.commit()
        
        return None
    
    def list(self):
        'method to read table subjects into a list'
        cursor = self.util._conn.cursor()  
        try:
            cursor.execute("""SELECT * from uri_status""")
        except (Exception, psycopg2.Error) as error :
            print ("not able to execute the select: %s " % error)
        
        results = cursor.fetchall()
        return results

if __name__ == "__main__":
    pass    