'''
.. include:: ../../README.md

# Library functions
'''

__PROJECT__ = 'pyDictStore'
__VERSION__ = '1.0.0'

from .__decorators__ import default, storageSetter, storage

def isDefault(obj:object,prop:str) -> bool:
    '''
    Checks if an objects property is equal to its default value
    '''
    return getattr(obj,prop) == getDefault(obj,prop)
    
def getDefault(obj:object,prop:str) -> object:
    '''
    Returns the default value of an objects property
    '''
    t = type(obj)
    return getattr(type(obj)(),prop)