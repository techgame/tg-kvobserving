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
#~ KV List Implementation 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVList(list, KVObject):
    def _prop_set_(self, prop, host, value):
        if isinstance(value, type(self)):
            return prop.set(host, value)
        else:
            self[:] = value

    def copy(self):
        return type(self)(self)

    def __setitem__(self, i, item): 
        list.__setitem__(self, i, item)
        self.kvpub.publish('*')
    def __delitem__(self, i): 
        list.__delitem__(self, i)
        self.kvpub.publish('*')
    def __setslice__(self, i, j, other):
        list.__setslice__(self, i, j, other)
        self.kvpub.publish('*')
    def __delslice__(self, i, j):
        list.__delslice__(self, i, j)
        self.kvpub.publish('*')

    def __iadd__(self, other):
        result = list.__iadd__(self, other)
        self.kvpub.publish('*')
        return result
    def __imul__(self, other):
        result = list.__imul__(self, other)
        self.kvpub.publish('*')
        return result
    def append(self, item):
        i = len(self)
        list.append(self, item)
        self.kvpub.publish('*')
    def insert(self, i, item):
        list.insert(self, i, item)
        self.kvpub.publish('*')
    def pop(self, i=-1):
        if i >= 0: ni = i
        else: ni = i + len(self)
        result = list.pop(self, i)
        self.kvpub.publish('*')
        return result
    def clear(self, item): 
        del self[:]
    def remove(self, item): 
        list.remove(self, item)
        self.kvpub.publish('*')
    def reverse(self):
        list.reverse(self)
        self.kvpub.publish('*')
    def sort(self, *args, **kwds): 
        list.sort(self, *args, **kwds)
        self.kvpub.publish('*')
    def extend(self, other):
        list.extend(self, other)
        self.kvpub.publish('*')
KVList.property = classmethod(kvObjProperty)


