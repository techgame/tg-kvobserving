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
#~ KV List Implementation 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVList(list, KVObject):
    def copy(self):
        return type(self)(self)

    def __setitem__(self, i, item): 
        list.__setitem__(self, i, item)
        self.kvpub('*')
    def __delitem__(self, i): 
        list.__delitem__(self, i)
        self.kvpub('*')
    def __setslice__(self, i, j, other):
        list.__setslice__(self, i, j, other)
        self.kvpub('*')
    def __delslice__(self, i, j):
        list.__delslice__(self, i, j)
        self.kvpub('*')

    def __iadd__(self, other):
        result = list.__iadd__(self, other)
        self.kvpub('*')
        return result
    def __imul__(self, other):
        result = list.__imul__(self, other)
        self.kvpub('*')
        return result
    def append(self, item):
        i = len(self)
        list.append(self, item)
        self.kvpub('*')
    def insert(self, i, item):
        list.insert(self, i, item)
        self.kvpub('*')
    def pop(self, i=-1):
        if i >= 0: ni = i
        else: ni = i + len(self)
        result = list.pop(self, i)
        self.kvpub('*')
        return result
    def remove(self, item): 
        list.remove(self, item)
        self.kvpub('*')
    def reverse(self):
        list.reverse(self)
        self.kvpub('*')
    def sort(self, *args, **kwds): 
        list.sort(self, *args, **kwds)
        self.kvpub('*')
    def extend(self, other):
        list.extend(self, other)
        self.kvpub('*')
KVList.property = classmethod(kvproperty)


