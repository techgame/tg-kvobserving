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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Property Implementation 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVProperty(OBProperty):
    """Publishes a key-value pair
    
    Can only be used on a KVObject-based instance"""
    _private_fmt = '__kv_%s'

    def fetchOnInit(self):
        self.__class__ = KVInitProperty
        return self

    def _modified_(self, obInst):
        obInst.kvpub.publishProp(self.public, obInst)

class KVInitProperty(KVProperty):
    def onObservableInit(self, propertyName, obInstance):
        self.__get__(obInstance, type(obInstance))
    onObservableInit.priority = -5


kvProperty = KVProperty.factoryMethod()
kvproperty = kvProperty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVObjectProperty(KVProperty):
    missing = None

    def __get__(self, obInst, obKlass):
        if obInst is None: return self

        dobj = KVProperty.__get__(self, obInst, obKlass)
        return dobj._prop_get_(self, obInst)

    def __set__(self, obInst, value):
        dobj = self.__get__(obInst, type(obInst))
        dobj._prop_set_(self, obInst, value)

    def __set_factory__(self, obInst, value):
        self.set(obInst, value)
        value._prop_init_(self, obInst, value)

    def fetchOnInit(self):
        self.__class__ = KVInitObjectProperty
        return self

class KVInitObjectProperty(KVObjectProperty):
    def onObservableInit(self, propertyName, obInstance):
        self.__get__(obInstance, type(obInstance))
    onObservableInit.priority = -5


kvObjProperty = KVObjectProperty.factoryMethod()

