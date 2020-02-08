'''
Created on 20180818
extra support and a better name
@author: Gerben Rienk
'''

from dictfile import readDictFile
    
if __name__ == '__main__':
    # read configuration file for usernames and passwords and other parameters
    config=readDictFile('odkoc4.config')
    print(config['apiUrl'])
    
    
