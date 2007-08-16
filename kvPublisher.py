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

from TG.metaObserving import OBKeyedSet

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVPublisher(object):
    pubName = 'kvpub'
    host = None

    def __init__(self):
        self.koset = OBKeyedSet()

    def __repr__(self):
        return '<%s to: %r>' % (self.__class__.__name__, self.koset)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onObservableClassInit(self, pubName, obKlass):
        self = self.copy()
        if pubName != self.pubName:
            self.pubName = pubName
        setattr(obKlass, pubName, self)
    onObservableClassInit.priority = -10

    def onObservableInit(self, pubName, obInstance):
        if pubName not in vars(obInstance):
            self.copyWithHost(obInstance, pubName)
    onObservableInit.priority = -10

    def copyWithHost(self, host, pubName=None):
        if host is None:
            return
        self = self.copy()
        self.host = ref(host, self._onHostExpire)
        setattr(host, pubName or self.pubName, self)
        return self

    def _onHostExpire(self, ref):
        self.host = None
        self.clear()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def new(klass):
        return klass.__new__(klass)

    def copy(self):
        result = self.new()
        return result.copyFrom(self)

    def copyFrom(self, other):
        if self.pubName != other.pubName:
            self.pubName = other.pubName

        self.koset = other.koset.copy()
        host = other.host
        if host is not None:
            self.host = ref(host(), self._onHostExpire)
        else: self.host = None
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
        if self.koset:
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

    def __call__(self, key, *args, **kw):
        if key.startswith('@'):
            return self.event(key, *args, **kw)
        else:
            return self.publish(key, *args, **kw)

    def event(self, key, *args, **kw):
        entry = self.koset.get(key)
        if entry:
            entry.call_ak(self.host(), key, *args, **kw)

    _kvqueue = None
    def publish(self, key):
        kvqueue = self._kvqueue
        if kvqueue is not None:
            kvqueue.append(key)
            return

        entry = self.koset.get(key)
        if entry:
            entry.call_n2(self.host(), key)

    def publishProp(self, key, host):
        if self.host is None:
            self = self.copyWithHost(host)
        self.publish(key)

    def publishAll(self, iterkeys):
        kvqueue = self._kvqueue
        if kvqueue is not None:
            kvqueue.extend(iterkeys)
            return

        koset = self.koset
        host = self.host()
        for key in iterkeys:
            entry = koset.get(key)
            if entry:
                entry.call_n2(host, key)

    def publishQue(self, kvqueue):
        keyset = set()
        self.publishAll((keyset.add(key), key)[1] 
                for key in kvqueue if key not in keyset)

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
            del self._ctxdepth

            if bPublish:
                self.publishQue(kvqueue)
            return kvqueue

        self._ctxdepth = depth
        return None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __enter__(self):
        self.acquire()
    def __exit__(self, exc=None, exc_type=None, exc_tb=None):
        self.release(exc is None)

