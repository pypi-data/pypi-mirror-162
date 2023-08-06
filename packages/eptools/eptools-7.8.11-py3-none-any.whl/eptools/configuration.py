import json
C_TESTGLOBAL = 1

def loadconfigwithjson(value):
    if type(value) == str:
        value = json.loads(value)
    all_variables = dir()
    for name in all_variables:
        if not name.startswith('C_'):
            myvalue = eval(name)
            if value.get(name,None):
                globals()[name]= value[name]
        
        
def loadconfigwithfile(value):
    with open(value,'r') as file:
        text = file.read()
        loadconfigwithjson(json.loads(text))