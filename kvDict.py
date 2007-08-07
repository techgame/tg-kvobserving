##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2007  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .kvObject import KVObject
from .kvProperty import kvproperty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Dict Implementation 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVDict(dict, KVObject):
    def copy(self):
        return type(self)(self)

    def __setitem__(self, key, item): 
        dict.__setitem__(self, key, item)
        self.kvpub.publish('*')
    def __delitem__(self, key): 
        dict.__delitem__(self, key)
        self.kvpub.publish('*')
    def clear(self): 
        dict.clear(self)
        self.kvpub.publish('*')
    def update(self, *args, **kwargs):
        dict.update(self, *args, **kwargs)
        self.kvpub.publish('*')
    def setdefault(self, key, failobj=None):
        if key in self:
            result = self.get(key)
        else:
            result = dict.setdefault(self, key, failobj)
            self.kvpub.publish('*')
        return result
    def pop(self, key, *args):
        if key in self:
            result = dict.pop(self, key)
            self.kvpub.publish('*')
        else:
            result = dict.pop(self, key, *args)
        return result
    def popitem(self):
        result = dict.popitem(self)
        self.kvpub.publish('*')
        return result
KVDict.property = classmethod(kvproperty)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVKeyedDict(dict, KVObject):
    def copy(self):
        return type(self)(self)

    def __setitem__(self, key, item): 
        dict.__setitem__(self, key, item)
        self.kvpub.publish(key)
    def __delitem__(self, key): 
        dict.__delitem__(self, key)
        self.kvpub.publish(key)
    def clear(self): 
        keys = self.keys()
        dict.clear(self)
        for k in keys:
            self.kvpub.publish(k)
    def update(self, *args, **kwargs):
        ud = dict()
        ud.update(*args, **kwargs)
        dict.update(self, ud)
        for k in ud.keys():
            self.kvpub.publish(k)
    def setdefault(self, key, failobj=None):
        if key in self:
            result = self.get(key)
        else:
            result = dict.setdefault(self, key, failobj)
            self.kvpub.publish(key)
        return result
    def pop(self, key, *args):
        if key in self:
            result = dict.pop(self, key)
            self.kvpub.publish(key)
        else:
            result = dict.pop(self, key, *args)
        return result
    def popitem(self):
        result = dict.popitem(self)
        self.kvpub.publish(result[0])
        return result
KVKeyedDict.property = classmethod(kvproperty)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVNamespace(KVKeyedDict):
    def __getattr__(self, name):
        return self[name]
    def __setattr__(self, name, value):
        self[name] = value
    def __delattr__(self, name):
        del self[name]

