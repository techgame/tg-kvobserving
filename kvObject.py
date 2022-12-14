##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2006  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from TG.metaObserving import MetaObservableType, OBFactoryMap, OBSettings
from .kvPublisher import KVPublisher

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVObjectType(MetaObservableType):
    """Subclass of ObservableType enabling subclassing and instantiation as
    cooperative events, and customization to the key-value observing design."""

class KVObject(object):
    """Subclass of object using KVObjectType as the metaclass so subclass
    declaration and class instantiation are observable events"""
    __metaclass__ = KVObjectType

    # kvpub is a class-variable which is cloned into subclass and instance
    # namespaces using KVObjectType's onObservableClassInit() and
    # onObservableInit() hooks
    kvpub = KVPublisher()

    # NOTE: These are added to KVObject by other modules
    def kvwatcher(self, kvpath=None):
        raise NotImplementedError('Provided by kvWatcher module')
    def kvwatch(obj, kvpath=None, notify=False):
        raise NotImplementedError('Provided by kvWatcher module')
    def kvo(rootOrPath, kvpath=None, notify=None):
        raise NotImplementedError('Provided by kvObserver module')

    def __setstate__(self, state):
        type(self).observerNotifyRestore(self)

