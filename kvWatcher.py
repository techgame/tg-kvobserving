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

from TG.metaObserving import OBSet, OBNamedAttribute
from .kvObject import KVObject
from .kvProperty import KVProperty
from .kvPathLink import KVPathLink

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Watcher using KVPathLink
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVWatcher(KVObject, KVPathLink):
    valueDefault = None
    vobs = KVProperty(OBSet)

    value = KVProperty(valueDefault)
    select = KVProperty(valueDefault)

    def __init__(self, root=None, kvpath=None, vobs=None):
        if vobs is not None:
            self.vobs = vobs
        KVPathLink.__init__(self, root, kvpath)

    def copyWithRoot(self, root):
        return self.__class__(root, self.kvpath, self.vobs.copy())

    def onObservableInit(self, pubName, obInstance):
        """Connect to the instance's kvpub when it is created"""
        self = self.copyWithRoot(obInstance)
    onObservableInit.priority = 5

    def onObservableRestore(self, pubName, obInstance):
        self.onObservableInit(pubName, obInstance)
    onObservableRestore.priority = onObservableInit.priority

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    def _onLinkEndpointChanged(self, host, key):
        if key not in self.kvOperators:
            value = getattr(host, key, self.valueDefault)
        else: value = host

        self.value = value
        self.vobs.call_n2(self, value)
    _onLinkWatched = _onLinkEndpointChanged

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        value = self.valueDefault
        self.value = value
        self.vobs.call_n2(self, value)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVWatchAttr(OBNamedAttribute, KVPathLink):
    _private_fmt = '__kvw_%s'
    valueDefault = None

    def __init__(self, kvpath, publish=None):
        OBNamedAttribute.__init__(self, publish)
        KVPathLink.__init__(self, None, kvpath)

    def initLink(self, root, kvpath):
        self.configLink(root, kvpath)

    def copy(self):
        return self.__class__(self.kvpath, self.public)

    def onObservableInit(self, pubName, obInstance):
        """Connect to the instance's kvpub when it is created"""
        self = self.copy()
        setattr(obInstance, self.private, self)
        self.link(obInstance)
    onObservableInit.priority = 5

    def onObservableRestore(self, pubName, obInstance):
        self.onObservableInit(pubName, obInstance)
    onObservableRestore.priority = onObservableInit.priority

    def _onLinkEndpointChanged(self, host, key):
        if key not in self.kvOperators:
            value = getattr(host, key, self.valueDefault)
        else: value = host
        self.publish(value)
    _onLinkWatched = _onLinkEndpointChanged

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        self.publish(self.valueDefault)

    def publish(self, value):
        setattr(self.root, self.public, value)
        self.root.kvpub.publish(self.public)

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

