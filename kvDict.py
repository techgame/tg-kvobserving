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
from .kvProperty import kvObjProperty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Dict Implementation 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVDict(dict, KVObject):
    def _prop_init_(self, prop, host, value):
        pass
    def _prop_get_(self, prop, host):
        return self
    def _prop_set_(self, prop, host, value):
        if isinstance(value, type(self)):
            return prop.set(host, value)
        else:
            dict.clear(self)
            self.update(value)

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
KVDict.property = classmethod(kvObjProperty)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVKeyedDict(dict, KVObject):
    def _prop_init_(self, prop, host, value):
        pass
    def _prop_get_(self, prop, host):
        return self
    def _prop_set_(self, prop, host, value):
        if isinstance(value, type(self)):
            return prop.set(host, value)
        else:
            keys = set(self.iterkeys())
            dict.clear(self)
            dict.update(self, value)
            keys.update(self.iterkeys())
            self.kvpub.publishAll(keys)

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
        self.kvpub.publishAll(keys)
    def update(self, *args, **kwargs):
        ud = dict()
        ud.update(*args, **kwargs)
        dict.update(self, ud)
        self.kvpub.publishAll(ud.iterkeys())
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
KVKeyedDict.property = classmethod(kvObjProperty)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVNamespace(KVKeyedDict):
    def __getattr__(self, name):
        if name in type(self).__dict__:
            return KVKeyedDict.__getattr__(self, name)

        try:
            return self[name]
        except LookupError, e:
            raise AttributeError(str(e))

    def __setattr__(self, name, value):
        if name in type(self).__dict__:
            return KVKeyedDict.__setattr__(self, name, value)

        try:
            self[name] = value
        except LookupError, e:
            raise AttributeError(str(e))

    def __delattr__(self, name):
        if name in type(self).__dict__:
            return KVKeyedDict.__delattr__(self, name)

        try:
            del self[name]
        except LookupError, e:
            raise AttributeError(str(e))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVObjectNS(KVObject):
    ns = None

    def __init__(self):
        self.ns = KVKeyedDict()
        self.ns.kvpub = self.kvpub

    def __getattr__(self, name):
        try:
            return self.ns[name]
        except LookupError, e:
            raise AttributeError(str(e))

    def __setattr__(self, name, value):
        if name in type(self).__dict__:
            return KVObject.__setattr__(self, name, value)

        try:
            self.ns[name] = value
        except LookupError, e:
            raise AttributeError(str(e))

    def __delattr__(self, name):
        if name in type(self).__dict__:
            return KVObject.__delattr__(self, name)

        try:
            del self.ns[name]
        except LookupError, e:
            raise AttributeError(str(e))

