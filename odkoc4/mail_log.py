'''
Created on 20200123
based on the oc3 version
@author: Gerben Rienk
'''
import datetime

from utils.dictfile import readDictFile
from utils.logmailer import Mailer
from utils.reporter import Reporter

def find_and_mail_log():
    # create or re-use a log file to write actions and messages
    this_date = datetime.datetime.now()
    date_stamp = this_date.strftime("%Y%m%d")
    report_name = 'logs/odkoc4_%s.log' % date_stamp 
    my_report = Reporter(report_name)
    
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
        
    # set up the mailer
    my_mailer = Mailer(config)
    # send the report
    my_mailer.send_file(report_name)
    
if __name__ == '__main__':
    find_and_mail_log()

