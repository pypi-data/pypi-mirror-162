from .__events__ import PropertyChangedEvent
class storage:
    def __init__(self, cls) -> None:
        self.cls = cls

    def __call__(self, *args, **kwargs):
        # #Add storage variable to the object instance
        def decorate(fcn):
            def __new__(cls,*args, **kwargs):
                oCls = super(type(cls), cls).__new__(cls)
                oCls.__storage__ = {}
                cls.PropertyChanged = PropertyChangedEvent()
                from typing import cast
                return cast(type(cls),oCls)
            return __new__
        self.cls.__new__ = decorate(self.cls.__new__)
        #Add storageSet and default(none) to properties if not already present
        for name in [p for p in dir(self.cls) if isinstance(getattr(self.cls,p),property)]:
            prop = getattr(self.cls,name)
            fget = (prop.fget 
                    if prop.fget.__qualname__ == 'default.__call__.<locals>.wrapper'
                    else default(None)(prop.fget)
                    )
            fset = (prop.fset 
                    #if prop.fset.__qualname__ == 'storageSetter.<locals>.wrapper'
                    if isinstance(prop.fset,storageSetter)
                    else storageSetter(prop.fset)
                    )
            setattr(self.cls, name, property(fget, fset, prop.fdel))  
        return self.cls()

class default:
    def __init__(self, value=None) -> None:
        self.value = value

    def __call__(self, function):
        def wrapper(*args, **kwargs):
            obj = args[0]
            v = self.value
            if hasattr(obj,'__storage__'): 
                strg = getattr(obj, '__storage__')
                if not function.__name__ in strg:
                    strg[function.__name__] = self.value
                v = strg[function.__name__]
            vOverride = function(*args, **kwargs)
            return v if vOverride is None else vOverride
        return wrapper

class storageSetter:
    def __init__(self, function) -> None:
        self.function = function

    def __call__(self, *args, **kwargs):
        obj = args[0]
        value = args[1]
        oValue = self.function(*args, **kwargs)
        if hasattr(obj,'__storage__'): 
            strg = getattr(obj, '__storage__')
            oldValue=getattr(obj, self.function.__name__)
            strg[self.function.__name__] = value if oValue is None else oValue
            if hasattr(obj,'PropertyChanged'):
                obj.PropertyChanged(
                            obj
                            ,self.function.__name__
                            , oldValue
                            , getattr(obj, self.function.__name__) #newValue
                            )