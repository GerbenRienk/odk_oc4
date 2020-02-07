'''
Created on 20200123
based on the oc3 version
@author: Gerben Rienk
'''
from utils.logmailer import Mailer
from utils.dictfile import readDictFile
from utils.reporter import Reporter

def cycle_through_syncs():
    config=readDictFile('odkoc4.config')
    my_report = Reporter()
    my_mailer = Mailer(config)
    my_report.append_to_report('test line')
    # close the file so we can send it
    my_report.close_file()
    my_mailer.send_file('logs/report.txt')
    
    
if __name__ == '__main__':
    cycle_through_syncs()

