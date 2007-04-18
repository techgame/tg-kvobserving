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

class KVObserver(KVPathLink):
    valueDefault = None
    notify = None

    def onObservableInit(self, pubName, obInstance):
        """Connect to the instance's kvpub when it is created"""
        self.link(root=obInstance)
    onObservableInit.priority = 5

    def decorate(self, notify):
        self.notify = notify
        if self.root is None:
            notify.onObservableInit = self.onObservableInit
        self.link()
        return notify

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _onLinkValueChanged(self, host, key):
        if key not in self.kvOperators:
            value = getattr(host, key, self.valueDefault)
        else: value = host
        self._callNotify(value)
    _onLinkWatched = _onLinkValueChanged

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        if self.isLinkable():
            self._callNotify(self.valueDefault)

    def _callNotify(self, value):
        notify = self.notify
        if notify is not None:
            notify(self.root, value)

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

    obs = KVObserver(root, kvpath)
    if notify is not None:
        return obs.decorate(notify)
    else: 
        return obs.decorate

KVObject.kvo = kvobserve
KVObject.kvobserve = classmethod(kvobserve)

