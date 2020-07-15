'''
Created on 20180818

@author: GerbenRienk
'''
import os

class Reporter(object):
    '''
    Reporter object that creates a file
    to which lines can be added reporting the activities of oodkoc4,
    so it can be sent at the end of the day
    '''

    def __init__(self, report_name='logs/report.txt'):
        '''
        Constructor
        '''
        self.report_name=report_name
        if os.path.exists(report_name):
            mode = 'a'
        else:
            mode = 'w'
        self._file = open(report_name, mode) 
        self._file.close()
        
        
    def append_to_report(self, report_line):
        '''before we write a new line to the report, we want to check if it's not already there'''
        report_line = report_line + '\n'
        add_this_line = True
        with open(self.report_name, 'r') as f:
            for line in f:
                if(report_line == line):
                    add_this_line = False
        
        # now we have the contents, so we can check if the line we want to add is already present
        if(add_this_line):
            with open(self.report_name, 'a') as f:
                f.write(report_line)
                
        return None
    
    def close_file(self):
        self._file.close()
        return None