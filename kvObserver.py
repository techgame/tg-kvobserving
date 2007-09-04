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

def addMethodObserverable(method, observer):
    observers = getattr(method, 'observers', [])
    observers.append(observer)
    setattr(method, 'observers', observers)

    initFns = [e.onObservableInit for e in observers if hasattr(e, 'onObservableInit')]
    def onObservableInit(pubName, obInstance, initFns=initFns):
        for onObservableInit in initFns:
            onObservableInit(pubName, obInstance)
    method.onObservableInit = onObservableInit

    restoreFns = [e.onObservableRestore for e in observers if hasattr(e, 'onObservableRestore')]
    def onObservableRestore(pubName, obInstance, restoreFns=restoreFns):
        for onObservableRestore in restoreFns:
            onObservableRestore(pubName, obInstance)
    method.onObservableRestore = onObservableRestore
    return method

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVBaseObserver(KVPathLink):
    notify = None
    updateOnInit = False

    def initLink(self, root, kvpath):
        self.configLink(root, kvpath)

    def copyWithRoot(self, root, updateLink=False):
        result = self.__class__(root, self.kvpath)
        result.setNotify(self.notify, updateLink)
        return result

    def onObservableInit(self, pubName, obInstance):
        """Connect to the instance's kvpub when it is created"""
        self = self.copyWithRoot(obInstance, self.updateOnInit)
    onObservableInit.priority = 5

    def onObservableRestore(self, pubName, obInstance):
        self = self.copyWithRoot(obInstance, False)
    onObservableRestore.priority = onObservableInit.priority

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def setNotify(self, notify, updateLink=True):
        self.notify = notify
        if self.root is None:
            self.addMethodObserverable(notify, self)
        else: self.link(updateLink=updateLink)
        return notify

    addMethodObserverable = staticmethod(addMethodObserverable)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Value Observer
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVValueObserver(KVBaseObserver):
    valueDefault = None
    updateOnInit = True

    def _onLinkEndpointChanged(self, host, key):
        if key in self.kvOperators:
            value = host
        else: 
            value = getattr(host, key, self.valueDefault)

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

