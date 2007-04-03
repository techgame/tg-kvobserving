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
    def __init__(self, notify=None, root=None, kvpath=None):
        self.notify = notify
        KVPathLink.__init__(self, root, kvpath)

    def onObservableInit(self, pubName, obInstance):
        self.link(root=obInstance)
    onObservableInit.priority = 5

    @classmethod
    def fromKVPath(klass, kvpath):
        return klass(kvpath=kvpath)

    @classmethod
    def observe(klass, kvpath):
        self = klass.fromKVPath(kvpath)
        return self.decorate

    def decorate(self, notify):
        self.notify = notify
        notify.onObservableInit = self.onObservableInit
        return notify

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _onLinkValueChanged(self, host, key):
        if key not in self.kvOperators:
            value = getattr(host, key, self.valueDefault)
        else: value = host
        notify = self.notify
        if notify is not None:
            notify(host, value)

    _onLinkWatched = _onLinkValueChanged

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        notify = self.notify
        if notify is not None:
            notify(None, self.valueDefault)

kvo = KVObserver.observe
KVObject.kvo = kvo

