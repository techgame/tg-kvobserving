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

    def onObservableClassInit(self, propertyName, obKlass):
        if self.public == True:
            # true signifies that this is a protected reflection of a public
            # name... just remove the leading underscores
            propertyName = propertyName.split('__', 1)
            if len(propertyName) > 1:
                propertyName = propertyName[1]
            else: propertyName = propertyName[0].lstrip('_')

        self._setPublishName(propertyName)
    onObservableClassInit.priority = OBProperty.onObservableClassInit.priority

    def _modified_(self, obInst):
        obInst.kvpub.publishProp(self.public, obInst)

kvProperty = KVProperty.factoryMethod()
kvproperty = kvProperty

class KVInitProperty(KVProperty):
    def onObservableInit(self, propertyName, obInstance):
        self.__get__(obInstance, type(obInstance))
    onObservableInit.priority = -5
kvInitProperty = KVProperty.factoryMethod()

class KVObjectProperty(KVProperty):
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

kvObjProperty = KVObjectProperty.factoryMethod()

