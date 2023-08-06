from .configuration import *

def loadconfigpath(path):
    loadconfigwithfile(path)
    
def load(value):
    loadconfigwithjson({"C_TESTGLOBAL":4})
    loadconfigwithjson("{\"C_TESTGLOBAL\":4}")
    
def dosimeting():
    print(C_TESTGLOBAL)