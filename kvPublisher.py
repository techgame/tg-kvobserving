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
from collections import defaultdict

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVPublisher(object):
    pubName = 'kvpub'

    def __init__(self):
        self.kvo = defaultdict(set)
        self.host = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onObservableClassInit(self, pubName, obKlass):
        selfCopy = self.copy()
        if pubName != self.pubName:
            self.pubName = pubName
        setattr(obKlass, pubName, selfCopy)

    def onObservableInit(self, pubName, obInstance):
        if self.host is None:
            self.copyWithHost(obInstance, pubName)

    def copyWithHost(self, host, pubName=None):
        if host is not None:
            wrhost = ref(host)
        selfCopy = self.copy()
        selfCopy.host = wrhost
        setattr(host, pubName or self.pubName, selfCopy)
        return selfCopy

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def copy(self):
        klass = type(self)
        result = klass.__new__(klass)
        return result.copyFrom(self)

    def copyFrom(self, other):
        self.kvo = self.kvoCopy(other.kvo)
        self.host = other.host
        return self

    def kvoCopy(self, other=None):
        kvo = defaultdict(set)
        if other is None:
            other = self.kvo
        if other:
            kvo.update((k, v.copy()) for k,v in other.iteritems())
        return kvo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __getitem__(self, key):
        return self.kvo[key]

    def on(self, key):
        return lambda kvObserver: self.add(key, kvObserver)
    def add(self, key, kvObserver):
        self.kvo[key].add(kvObserver)
        return kvObserver
    def remove(self, key, kvObserver):
        kvoEntry = self.kvo[key]
        kvoEntry.remove(kvObserver)
        if not kvoEntry:
            del self.kvo[key]
    def discard(self, key, kvObserver):
        kvoEntry = self.kvo[key]
        kvoEntry.discard(kvObserver)
        if not kvoEntry:
            del self.kvo[key]
    def clear(self, key=None):
        if key is None:
            self.kvo.clear()
        else:
            del self.kvo[key]

    def depend(self, key, otherKeys):
        if isinstance(otherKeys, basestring):
            otherKeys = [otherKeys]

        def pushDependency(host, okey):
            host.kvpub(key)

        kvo = self.kvo
        for okey in otherKeys:
            kvo[okey].add(pushDependency)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _kvqueue = None
    def publish(self, key, host=None):
        if host is not None and self.host is None:
            self = self.copyWithHost(host, self.pubName)

        kvqueue = self._kvqueue
        if kvqueue is not None:
            kvqueue.append(key)
            return

        kvoEntry = self.kvo.get(key)
        if kvoEntry:
            host = self.host()
            for e in kvoEntry.copy():
                e(host, key)
    __call__ = publish

    def publishQue(self, kvqueue, host=None):
        if host is not None and self.host is None:
            self = self.copyWithHost(host, self.pubName)

        # loop optimized version of publish()
        host = self.host()
        kvo = self.kvo

        visited = set()
        for key in kvqueue:
            if key in visited: 
                # already published
                continue
            else: visited.add(key)

            # visit as in publish()
            kvoEntry = kvo.get(key)
            if kvoEntry:
                for e in kvoEntry.copy():
                    e(host, key)

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

