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
#~ KV Set Implementation
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVSet(set, KVObject):
    def _prop_set_(self, prop, host, value):
        if isinstance(value, type(self)):
            return prop.set(host, value)
        else:
            set.clear(self)
            self.update(value)

    def copy(self):
        return type(self)(self)

    def add(self, item):
        set.add(self, item)
        self.kvpub.publish('*')

    def remove(self, item):
        set.remove(self, item)
        self.kvpub.publish('*')

    def discard(self, item):
        set.discard(self, item)
        self.kvpub.publish('*')

    def pop(self):
        result = set.pop(self)
        self.kvpub.publish('*')
        return result

    def clear(self):
        set.clear(self)
        self.kvpub.publish('*')

    def __ior__(self, other):
        set.__ior__(self, other)
        self.kvpub.publish('*')
        return self

    def update(self, other):
        set.update(self, other)
        self.kvpub.publish('*')

    def __iand__(self, other):
        set.__iand__(self, other)
        self.kvpub.publish('*')
        return self

    def intersection_update(self, other):
        set.intersection_update(self, other)
        self.kvpub.publish('*')

    def __isub__(self, other):
        set.__isub__(self, other)
        self.kvpub.publish('*')
        return self

    def difference_update(self, other):
        set.difference_update(self, other)
        self.kvpub.publish('*')

    def __ixor__(self, other):
        set.__ixor__(self, other)
        self.kvpub.publish('*')
        return self

    def symmetric_difference_update(self, other):
        set.symmetric_difference_update(self, other)
        self.kvpub.publish('*')

KVSet.property = classmethod(kvObjProperty)

