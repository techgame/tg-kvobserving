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
from .kvPathLink import KVPathLink

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVBaseObserver(KVPathLink):
    notify = None

    def initLink(self, root, kvpath):
        self.configLink(root, kvpath)

    def copyWithRoot(self, root, updateLink=False):
        result = self.__class__(root, self.kvpath)
        result.setNotify(self.notify, updateLink)
        return result

    _chainOnObservableInit = None
    def onObservableInit(self, pubName, obInstance):
        """Connect to the instance's kvpub when it is created"""
        chain = self._chainOnObservableInit
        if chain is not None:
            chain(pubName, obInstance)

        self = self.copyWithRoot(obInstance)
    onObservableInit.priority = 5

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def setNotify(self, notify, updateLink=True):
        self.notify = notify
        if self.root is None:
            self._chainOnObservableInit = getattr(notify, 'onObservableInit', None)
            notify.onObservableInit = self.onObservableInit
        else: self.link(updateLink=updateLink)
        return notify

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Value Observer
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVValueObserver(KVBaseObserver):
    valueDefault = None

    def _onLinkEndpointChanged(self, host, key):
        if key not in self.kvOperators:
            value = getattr(host, key, self.valueDefault)
        else: value = host
        self._callNotify(value)
    _onLinkWatched = _onLinkEndpointChanged

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        if self.isLinkable():
            self._callNotify(self.valueDefault)

    def _callNotify(self, value):
        notify = self.notify
        if notify is not None:
            notify(self.root, value)

KVObserver = KVValueObserver

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ EventObserver
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVEventObserver(KVBaseObserver):
    def _onLinkEndpointChanged(self, host, key, *args, **kw):
        notify = self.notify
        if notify is not None:
            notify(self.root, *args, **kw)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Event Hooking
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def kvobserve(rootOrPath, kvpath=None, notify=None):
    """KVObserver decorator that attaches to a method"""
    if kvpath is None:
        kvpath = rootOrPath
        root = None
    elif isinstance(rootOrPath, type): 
        # if this is a classmethod, then pretend that root was not passed
        root = None
    else:
        root = rootOrPath

    if '@' in kvpath:
        obs = KVEventObserver(root, kvpath)
    else:
        obs = KVValueObserver(root, kvpath)
    if notify is not None:
        return obs.setNotify(notify)
    else: 
        return obs.setNotify

KVObject.kvo = kvobserve
KVObject.kvobserve = classmethod(kvobserve)

