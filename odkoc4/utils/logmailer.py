'''
Created on 11 apr. 2017

@author: GerbenRienk
'''


# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText

class Mailer(object):
    '''Class for connecting to the postgresql database as defined in odkoc.config
    Methods implemented now are read subjects and add subjects '''
    def __init__(self, config):
        self.config = config
        if(config['mail_enabled'].lower() == "true"):
            self._mailit = True
        else:
            self._mailit = False        

    def send_file(self, LogFileName, prefix=''):
        # Open a plain text file for reading.  For this example, assume that
        # the text file contains only ASCII characters.
        with open(LogFileName) as fp:
            # Create a text/plain message
            msg = MIMEText(fp.read())
        
        msg['Subject'] = self.config[prefix + 'mail_subject'] + ' ' + self.config['environment']
        msg['From'] = self.config[prefix + 'mail_from']
        msg['To'] = self.config[prefix + 'mail_to']
        
        # Send the message via our own SMTP server,
        # but only if we can send mails
        if(self._mailit):
            mail_server = smtplib.SMTP(self.config['mail_server'])
            mail_server.send_message(msg)
            mail_server.quit()
        else:
            print("mail not enabled: we will print the message in stead")
            print(msg)
        
if __name__ == '__main__':
    pass