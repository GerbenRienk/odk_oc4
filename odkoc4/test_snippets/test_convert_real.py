item_value='123456789'
if(not item_value is None):
    _final_value = float(item_value)
else:
    _final_value = '*'
# on rare occasions we get a final value like 0E-31
if item_value.__contains__('E'):
    _final_value = '**'
print(_final_value)