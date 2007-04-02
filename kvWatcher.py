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

from .kvObject import KVObject
from .kvProperty import KVProperty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

kvOperators = {
    '*': '*', 
    '...': '*', 
    '[]': '*', 
    '{}': '*', 
    Ellipsis: '*',
    }

class KVPath(object):
    _kvpath_ = None
    _inplace_ = True

    def __init__(self, kvpath=None):
        if isinstance(kvpath, basestring):
            kvpath = [p for p in kvpath.split('.') if p]
        self._kvpath_ = list(kvpath or [])

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, '.'.join(self._kvpath_))

    def _add_path(self, *items):
        kvpath = self._kvpath_+list(items)
        if self._inplace_:
            self._kvpath_[:] = kvpath
            return self
        else:
            return type(self)(kvpath)

    def __len__(self):
        return len(self._kvpath_)
    def __iter__(self):
        return iter(self._kvpath_)

    def __getattr__(self, key):
        if key.endswith('__') or key.startswith('__'):
            return object.__getattr__(self, key)
        return self._add_path(kvOperators.get(key, key))
    def __setattr__(self, key, value):
        if key != '_kvpath_':
            raise AttributeError("KVPath attributes are read-only")

        object.__setattr__(self, key, value)
    def __call__(self, key):
        return self._add_path(kvOperators.get(key, key))
    def __getitem__(self, key):
        if isinstance(key, (int, long, slice)):
            return self._kvpath_[key]

        opkey = kvOperators.get(key, None)
        if opkey is not None:
            return self._add_path(opkey)

        raise ValueError("Ellipsis [...] is the only valid item for KVPath addresses")

    def __setitem__(self, key, value):
        if isinstance(key, (int, long, slice)):
            self._kvpath_[key] = value
        else:
            raise ValueError("Only index style indexing allowed in KVPath's setitem")
    __setslice__ = __setitem__

    def __delitem__(self, key):
        if isinstance(key, (int, long, slice)):
            del self._kvpath_[key]
        else:
            raise ValueError("Only index style indexing allowed in KVPath's delitem")
    __delslice__ = __delitem__

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

kv = KVPath()
vars(kv).update(_inplace_=False)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVPathLink(object):
    kvOperators = kvOperators
    asKVPath = KVPath

    def __init__(self, root=None, kvpath=None):
        self._kvlinks = []
        self.link(root, kvpath)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, '.'.join(self.kvpath._kvpath_))

    def link(self, root=NotImplemented, kvpath=NotImplemented):
        # unlink if we have a current link
        if self._kvlinks:
            self.unlink()

        # clear our link table
        self._kvlinks[:] = []
        kvlinks = self._kvlinks
        
        # setup our starting kvobj and kvpath
        if root is not NotImplemented:
            self.root = root
        else: root = self.root
        if kvpath is not NotImplemented:
            self.kvpath = self.asKVPath(kvpath)

        kvobj = root
        kvpath = list(self.kvpath)

        if root is None or not kvpath:
            # the root kvobj is missing... just note it so it can be updated later
            kvlinks.append((key, None))
            self._linkWatcher(kvlinks)

            self._onLinkIncomplete(None, None, kvpath)
            return None

        # for all the observable objects in the path
        for key in kvpath[:-1]:
            # get the next object in the kvpath, so we don't accidently trigger ourself in with a lazy-create attribute
            kvobjNext = getattr(kvobj, key, None)

            # add ourself to the kvpub for the key to get notified with the path changes
            kvpub = getattr(kvobj, 'kvpub', None)
            if kvpub is None:
                raise AttributeError("No valid kvpub found for %r at key:%r in path:%r" % (kvobj, key, kvpath))

            kvlinks.append((key, kvpub))

            if kvobjNext is None:
                # the kvobj is missing... just note it so it can be updated later
                kvlinks.append((key, None))
                self._linkWatcher(kvlinks)

                self._onLinkIncomplete(kvobj, key, kvpath)
                return False
            else:
                kvobj = kvobjNext

        # the last object in the path may or may not be observable
        key = kvpath[-1]

        # add ourself to the kvpub, but with the value callback
        kvpub = getattr(kvobj, 'kvpub', None)
        if kvpub is None:
            raise AttributeError("No valid kvpub found for %r at key:%r in path:%r" % (kvobj.__class__, key, kvpath))

        kvlinks.append((key, kvpub))
        self._linkWatcher(kvlinks)

        # send out the linkWatched notification
        self._onLinkWatched(kvobj, key)
        return True

    def _linkWatcher(self, kvlinks):
        for key, kvpub in kvlinks[:-1]:
            kvpub.add(key, self._onLinkPathChanged)

        key, kvpub = kvlinks[-1]
        if kvpub is not None:
            kvpub.add(key, self._onLinkValueChanged)

    def unlink(self):
        kvlinks = self._kvlinks[:]
        self._kvlinks[:] = []

        for key, kvpub in kvlinks[:-1]:
            kvpub.remove(key, self._onLinkPathChanged)

        key, kvpub = kvlinks[-1]
        if kvpub is not None:
            kvpub.remove(key, self._onLinkValueChanged)

    # link will call unlink if _kvlinks is not empty
    relink = link 

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _onLinkPathChanged(self, host, key):
        self.relink()

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        pass

    def _onLinkWatched(self, host, key):
        pass

    def _onLinkValueChanged(self, host, key):
        pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KV Watcher using KVPathLink
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVWatcher(KVObject, KVPathLink):
    valueDefault = None
    value = KVProperty(valueDefault)
    select = KVProperty(valueDefault)

    def add(self, valueObserver):
        self.kvpub.add('value', valueObserver)
        return valueObserver
    def remove(self, valueObserver):
        self.kvpub.remove('value', valueObserver)
        return valueObserver
    def clear(self):
        self.kvpub.clear('value')

    def addAndNotify(self, valueObserver):
        valueObserver(self, 'value')
        return self.add(valueObserver)
        

    def _onLinkValueChanged(self, host, key):
        if key in self.kvOperators:
            value = host
        else: 
            value = getattr(host, key, self.valueDefault)

        self.value = value
    _onLinkWatched = _onLinkValueChanged

    def _onLinkIncomplete(self, linkHost, key, kvpath):
        self.value = self.valueDefault

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Extend KVObject
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def kvwatcher(obj, kvpath=None):
    """Returns a KVWatcher instance, rooted on this object, watching kvpath"""
    return KVWatcher(obj, kvpath)
KVObject.kvwatcher = kvwatcher

def kvwatch(obj, kvpath=None, notify=False):
    """Instantiates a KVWatcher instance, and returns a decorator compatible add method"""
    watcher = obj.kvwatcher(kvpath)
    if notify:
        return watcher.addAndNotify
    else: return watcher.add
KVObject.kvwatch = kvwatch

