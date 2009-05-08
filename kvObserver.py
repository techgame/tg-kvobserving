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
    del observers

    def onObservableInit(pubName, obInstance):
        for e in method.observers:
            obsInit = getattr(e, 'onObservableInit', None)
            if obsInit is not None:
                obsInit(pubName, obInstance)
    method.onObservableInit = onObservableInit

    def onObservableRestore(pubName, obInstance):
        for e in method.observers:
            obsRestore = getattr(e, 'onObservableRestore', None)
            if obsRestore is not None:
                obsRestore(pubName, obInstance)
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
        if notify is None: return

        root = self.root
        if root is None: return

        notify(root, value)

KVObserver = KVValueObserver

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ EventObserver
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVEventObserver(KVBaseObserver):
    def _onLinkEndpointChanged(self, host, key, *args, **kw):
        notify = self.notify
        if notify is None: return

        root = self.root
        if root is None: return

        notify(root, *args, **kw)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Event Hooking
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def kvobserve(rootOrPath, kvpath=None, notify=None, asDecorator=True):
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
        r = obs.setNotify(notify)
        if asDecorator:
            return r
    elif asDecorator:
        return obs.setNotify

    return obs

KVObject.kvo = kvobserve
KVObject.kvobserve = classmethod(kvobserve)

