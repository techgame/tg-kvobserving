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

from TG.metaObserving import OBSet
from .kvObject import KVObject
from .kvProperty import KVProperty
from .kvPathLink import KVPathLink

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Watcher using KVPathLink
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVWatcher(KVObject, KVPathLink):
    valueDefault = None
    value = KVProperty(valueDefault)
    vobs = KVProperty(OBSet)

    select = KVProperty(valueDefault)

    def add(self, observer):
        self.vobs.add(observer)
        return observer
    def remove(self, observer):
        self.vobs.remove(observer)
        return observer
    def clear(self):
        self.vobs.clear()

    def addAndNotify(self, observer):
        observer(self, self.value)
        return self.add(observer)

    def _onLinkValueChanged(self, host, key):
        if key not in self.kvOperators:
            value = getattr(host, key, self.valueDefault)
        else: value = host

        self.value = value
        self.vobs.call_n2(self, value)
    _onLinkWatched = _onLinkValueChanged

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        value = self.valueDefault
        self.value = value
        self.vobs.call_n2(self, value)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Extend KVObject
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def kvwatcher(obj, kvpath=None):
    """Returns a KVWatcher instance, rooted on this object, watching kvpath"""
    return KVWatcher(obj, kvpath)
KVObject.kvwatcher = kvwatcher

def kvwatch(obj, kvpath=None, notify=False):
    """Instantiates a KVWatcher instance, and returns a decorator compatible add method"""
    watcher = obj.kvwatcher(kvpath)
    if notify:
        return watcher.addAndNotify
    else: return watcher.add
KVObject.kvwatch = kvwatch

