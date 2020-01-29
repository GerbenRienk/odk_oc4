'''
To read a dictionary from file
Comments are preceded with a #
Empty lines are ignored
Error handling for lines with more than 2 splits should be implemented
All files should be placed in folder "config"
@author: Gerben Rienk
'''
import json

if __name__ == '__main__':
    pass

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except:
        return False