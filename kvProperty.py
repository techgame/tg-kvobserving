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

from TG.metaObserving import OBProperty
from .kvObject import KVObjectType, KVObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Property Implementation 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVProperty(OBProperty):
    """Publishes a key-value pair
    
    Can only be used on a KVObject-based instance"""
    def __init__(self, factory=NotImplemented, isValue=None, publish=None):
        if publish:
            self.public = publish
        OBProperty.__init__(self, factory, isValue)

    def onObservableClassInit(self, propertyName, obKlass):
        if self.public is None:
            self.public = propertyName
        elif self.public == True:
            # true signifies that this is a protected reflection of a public
            # name... just remove the leading underscores
            propertyName = propertyName.split('__', 1)
            if len(propertyName) > 1:
                propertyName = propertyName[1]
            else: propertyName = propertyName[0].lstrip('_')

            self.public = propertyName

        self.private = "__kv_"+propertyName

    def _modified_(self, obInst):
        obInst.kvpub(self.public, obInst)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Extend KVObjectType
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def kvproperty(kvObjectFactory, *args, **kw):
    if args or kw:
        instFactory = lambda: kvObjectFactory(*args, **kw)
    else: instFactory = kvObjectFactory
    return KVProperty(instFactory)
KVObjectType.kvproperty = kvproperty

