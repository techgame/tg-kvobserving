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
        self.link(root=obInstance)
    onObservableInit.priority = 5

    def decorate(self, notify):
        self.notify = notify
        if self.root is None:
            notify.onObservableInit = self.onObservableInit
        return notify

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _onLinkValueChanged(self, host, key):
        if key not in self.kvOperators:
            value = getattr(host, key, self.valueDefault)
        else: value = host
        self._callNotify(host, value)
    _onLinkWatched = _onLinkValueChanged

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        self._callNotify(None, self.valueDefault)

    def _callNotify(self, host, value):
        notify = self.notify
        if notify is not None:
            notify(host, value)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def kvobserve(rootOrPath, kvpath=None):
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
    return obs.decorate

KVObject.kvo = kvobserve
KVObject.kvobserve = classmethod(kvobserve)

