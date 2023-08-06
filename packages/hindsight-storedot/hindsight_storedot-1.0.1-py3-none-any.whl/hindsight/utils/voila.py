from urllib.parse import parse_qsl
from os import environ
from json import loads, JSONDecodeError
from functools import reduce

class QueryParams(object):
    NESTED_PARAM_DELIMITER = '.'
    VOILA_QUERY_KEY = 'QUERY_STRING'
    
    def __init__(self, global_ref: dict):
        self.params = QueryParams.read()
        self.global_ref = global_ref
        
    @classmethod
    def read(cls):
        query = environ.get(QueryParams.VOILA_QUERY_KEY, '')

        params = dict(parse_qsl(query))

        for key, value in params.items():
            try:
                params.update({
                    key: loads(value)
                })

            except JSONDecodeError:
                pass

        return params
    
    def set_variables(self):
        for key in list(self.params.keys()): #Iterate a copy!
            split_key = list(
                filter(None, key.split(QueryParams.NESTED_PARAM_DELIMITER))
            ) # Split into Var and nested Attrs
            
            target = self.global_ref.get(split_key[0]) # Only the first part is a declared Var
            
            if not target:
                continue
            
            value = self.params.pop(key, None) # Variable should only be set Once!
            
            try:
                attributes = split_key[1:]
                target_attr = attributes.pop() # Last one is the variable
                nested_target = reduce(getattr, attributes, target)
                
                setattr(nested_target, target_attr, value)
                
            except IndexError:
                # Key is a variable
                self.global_ref[key] = value
                
            except Exception as e:
                print(e)
