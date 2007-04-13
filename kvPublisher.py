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

from weakref import ref

from TG.metaObserving import observerSet

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVPublisher(object):
    KeyedObserverSet = observerSet.KeyedObserverSet
    pubName = 'kvpub'

    def __init__(self):
        self.koset = self.KeyedObserverSet()
        self.host = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onObservableClassInit(self, pubName, obKlass):
        selfCopy = self.copy()
        if pubName != self.pubName:
            self.pubName = pubName
        setattr(obKlass, pubName, selfCopy)
    onObservableClassInit.priority = -10

    def onObservableInit(self, pubName, obInstance):
        if pubName not in vars(obInstance):
            self.copyWithHost(obInstance, pubName)
    onObservableInit.priority = -10

    def copyWithHost(self, host, pubName=None):
        if host is None:
            return
        wrhost = ref(host)
        selfCopy = self.copy()
        selfCopy.host = wrhost
        setattr(host, pubName or self.pubName, selfCopy)
        return selfCopy

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def new(klass):
        return klass()

    def copy(self):
        result = self.new()
        return result.copyFrom(self)

    def copyFrom(self, other):
        self.koset = other.koset.copy()
        self.host = other.host
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __getitem__(self, key):
        return self.koset[key]
    def change(self, bAdd, key, kvObserver):
        return self.koset.change(bAdd, key, kvObserver)
    def add(self, key, kvObserver):
        return self.koset.add(key, kvObserver)
    def remove(self, key, kvObserver):
        return self.koset.remove(key, kvObserver)
    def discard(self, key, kvObserver):
        return self.koset.discard(key, kvObserver)
    def clear(self, key=None):
        return self.koset.clear(key)

    def on(self, key):
        return lambda kvObserver: self.add(key, kvObserver)

    def depend(self, key, otherKeys):
        def pushDependency(host, okey, depKey=key):
            host.kvpub(depKey)

        if isinstance(otherKeys, basestring):
            otherKeys = [otherKeys]

        koset = self.koset
        for okey in otherKeys:
            koset[okey].add(pushDependency)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _kvqueue = None
    def publish(self, key, host=None):
        if host is not None and self.host is None:
            self = self.copyWithHost(host, self.pubName)

        kvqueue = self._kvqueue
        if kvqueue is not None:
            kvqueue.append(key)
            return

        entry = self.koset.get(key)
        if entry:
            host = self.host()
            entry.call_n2(host, key)
    __call__ = publish

    def publishQue(self, kvqueue, host=None):
        if host is not None and self.host is None:
            self = self.copyWithHost(host, self.pubName)

        # loop optimized version of publish()
        host = self.host()
        koset = self.koset

        visited = set()
        for key in kvqueue:
            if key in visited: 
                # already published
                continue
            else: visited.add(key)

            # visit as in publish()
            entry = koset.get(key)
            if entry:
                entry.call_n2(host, key)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Locking access
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _ctxdepth = 0

    def acquire(self):
        depth = self._ctxdepth + 1
        if depth == 1:
            self._kvqueue = []

        self._ctxdepth = depth

    def release(self, bPublish=True):
        depth = self._ctxdepth - 1
        if depth == 0:
            kvqueue = self._kvqueue
            del self._kvqueue

            if bPublish:
                self.publishQue(kvqueue)

            del self._ctxdepth

            return kvqueue

        self._ctxdepth = depth
        return None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __enter__(self):
        self.acquire()
    def __exit__(self, exc=None, exc_type=None, exc_tb=None):
        self.release(exc is None)

