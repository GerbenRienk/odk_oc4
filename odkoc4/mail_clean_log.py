'''
Created on 20200123
based on the oc3 version
@author: Gerben Rienk
'''
import datetime

from utils.dictfile import readDictFile
from utils.logmailer import Mailer
from utils.reporter import Reporter

def find_and_mail_clean_log():
    # create or re-use a log file to write actions and messages
    this_date = datetime.datetime.now()
    date_stamp = this_date.strftime("%Y%m%d")
    log_name = 'logs/odkoc4_%s.log' % date_stamp 
    clean_log_name = 'logs/odkoc4_clean_%s.log' % date_stamp
    my_clean_log = Reporter(clean_log_name)
    # my_report = Reporter(log_name)
    messages = {'preparing connections in','try to connect to', 'cycle started at', 
                'finished looping ', 'submitting data of', 'enrolment check', 'data were imported for'}

    with open(log_name, 'r') as f:
        all_these_lines = f.readlines()
        sorted_lines = sorted(all_these_lines) 
    
    for line in sorted_lines:
        # by default write the line, but ...
        write_this_line = True
        # but loop through the suppress-messages
        for message in messages:
            if line.__contains__(message):
                write_this_line = False
        # don't write empty lines
        if line == '\n':
            write_this_line = False
            
        if write_this_line:
            my_clean_log.append_to_report(line)
                

    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    # set up the mailer
    my_mailer = Mailer(config)
    # send the report
    my_mailer.send_file(clean_log_name, prefix='clean_')
    
if __name__ == '__main__':
    find_and_mail_clean_log()

