import json




def add_item( validation: dict  ):

    validation['success'] = validation['success'] and False 

    if 'validation' not in validation: validation['validation'] = []
    validation['validation'].append( { 'rule':'is_url', 'value':'23', 'result':False } )


validation = { 'success':True}
print("BEFORE")
print( json.dumps( validation ))
print("AFTER")
add_item(validation)
print( json.dumps( validation ))
