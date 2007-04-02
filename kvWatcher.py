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

from .kvObject import KVObject
from .kvProperty import KVProperty
from .kvPathLink import KVPathLink

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Watcher using KVPathLink
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVWatcher(KVObject, KVPathLink):
    valueDefault = None
    value = KVProperty(valueDefault)
    select = KVProperty(valueDefault)

    def add(self, valueObserver):
        self.kvpub.add('value', valueObserver)
        return valueObserver
    def remove(self, valueObserver):
        self.kvpub.remove('value', valueObserver)
        return valueObserver
    def clear(self):
        self.kvpub.clear('value')

    def addAndNotify(self, valueObserver):
        valueObserver(self, 'value')
        return self.add(valueObserver)
        

    def _onLinkValueChanged(self, host, key):
        if key in self.kvOperators:
            value = host
        else: 
            value = getattr(host, key, self.valueDefault)

        self.value = value
    _onLinkWatched = _onLinkValueChanged

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        self.value = self.valueDefault

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

