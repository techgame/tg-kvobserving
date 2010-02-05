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
from .kvDispatcher import KVDispatcher

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def unique(iterable):
    seen = set()
    for e in iterable:
        if e not in seen:
            seen.add(e)
            yield e
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVPublisher(object):
    pubName = 'kvpub'
    host = None

    def __init__(self):
        self.koset = OBKeyedSet()

    def __getstate__(self):
        return (self.pubName, self.host())
    def __setstate__(self, (pubName, host)):
        self.koset = OBKeyedSet()
        if host is not None:
            if isinstance(host, ref):
                host = host()
            self.copyWithHost(host, pubName)

    def __repr__(self):
        return '<%s to: %r>' % (self.__class__.__name__, self.koset)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    KVDispatcher = KVDispatcher
    def _bindDispatcher(self):
        return self.KVDispatcher(self.host)

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

    def onObservableRestore(self, pubName, obInstance):
        self.onObservableInit(pubName, obInstance)
    onObservableRestore.priority = onObservableInit.priority

    def copyWithHost(self, host, pubName=None):
        if host is None:
            return
        self = self.copy()
        return self._setHost(host, pubName or self.pubName)

    def _setHost(self, host, pubName):
        self.host = ref(host, self._onHostExpire)
        setattr(host, pubName, self)
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
        disp = self._bindDispatcher()
        if key.startswith('@'):
            self._bindEvent(key, disp)
        else:
            self._bindPublish(key, disp)

        if disp:
            if args or kw:
                disp.callEx(*args, **kw)
            else: disp.call()

    def event(self, key, *args, **kw):
        disp = self._bindDispatcher()
        self._bindEvent(key, disp)
        if disp: 
            if args or kw:
                disp.callEx(*args, **kw)
            else: disp.call()

    def publish(self, key):
        disp = self._bindDispatcher()
        self._bindPublish(key, disp)
        if disp: disp.call()

    def publishAll(self, iterkeys):
        disp = self._bindDispatcher()
        self._bindPublishMany(iterkeys, disp)
        if disp: disp.call()

    def publishProp(self, key, host):
        if self.host is None:
            self = self.copyWithHost(host)
        self.publish(key)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _bindEvent(self, key, disp):
        entry = self.koset.get(key)
        if entry:
            disp.add(entry, key)

    _kvqueue = None
    def _bindPublish(self, key, disp):
        kvqueue = self._kvqueue
        if kvqueue is not None:
            kvqueue.append(key)
            return

        koset = self.koset
        if key != '*':
            entry = koset.get(key)
            if entry:
                disp.add(entry, key)

        allEntry = koset.get('*')
        if allEntry:
            disp.add(allEntry, key)

    def _bindPublishMany(self, iterkeys, disp):
        kvqueue = self._kvqueue
        if kvqueue is not None:
            kvqueue.extend(iterkeys)
            return

        koset = self.koset
        allEntry = koset.get('*')
        for key in iterkeys:
            if key != '*':
                entry = koset.get(key)
                if entry:
                    disp.add(entry, key)
            if allEntry:
                disp.add(allEntry, key)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Locking access
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _ctxdepth = 0

    def acquire(self):
        depth = self._ctxdepth + 1
        if depth == 1:
            self._kvqueue = []

        self._ctxdepth = depth

    def release(self, bPublish=True, bindDispatch=False):
        depth = self._ctxdepth - 1
        if depth != 0:
            self._ctxdepth = depth
            return None

        kvqueue = self._kvqueue
        del self._kvqueue
        del self._ctxdepth

        if bPublish:
            kvqueue = unique(kvqueue)
            disp = self._bindDispatcher()
            self._bindPublishMany(kvqueue, disp)
            if bindDispatch:
                return disp
            elif disp:
                disp.call()
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __enter__(self):
        self.acquire()
    def __exit__(self, exc=None, exc_type=None, exc_tb=None):
        disp = self.release(exc is None, True)
        if disp and exc is None:
            disp.call()

