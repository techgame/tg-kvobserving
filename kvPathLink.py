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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KVPathLink
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVPathLink(object):
    kvOperators = kvOperators

    def __init__(self, root=None, kvpath=None):
        self._kvlinks = []
        self.link(root, kvpath)

    def __del__(self):
        self.unlink()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, '.'.join(self.kvpath._kvpath_))

    def asKVPath(self, path):
        return KVPath(path)

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
            kvlinks.append((None, None))
            self._linkWatcher(kvlinks)

            self._onLinkIncomplete(None, None, kvpath)
            return None

        # for all the observable objects in the path
        for key in kvpath[:-1]:
            # get the next object in the kvpath, so we don't accidently trigger ourself in with a lazy-create attribute
            kvobjNext = getattr(kvobj, key, None)

            # add ourself to the kvpub for the key to get notified with the path changes
            kvpub = getattr(kvobj, 'kvpub', None)
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
        kvlinks.append((key, kvpub))
        self._linkWatcher(kvlinks)

        # send out the linkWatched notification
        self._onLinkWatched(kvobj, key)
        return True

    # link will call unlink if _kvlinks is not empty
    relink = link 

    def unlink(self):
        kvlinks = self._kvlinks[:]
        self._kvlinks[:] = []
        self._linkWatcher(kvlinks, False)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _linkWatcher(self, kvlinks, bAdd=True):
        for key, kvpub in kvlinks[:-1]:
            if kvpub is not None:
                kvpub.change(bAdd, key, self._onLinkPathChanged)

        key, kvpub = kvlinks[-1]
        if kvpub is not None:
            kvpub.change(bAdd, key, self._onLinkValueChanged)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _onLinkPathChanged(self, host, key): self.relink()
    def _onLinkIncomplete(self, linkHost, key, kvpath): pass
    def _onLinkWatched(self, host, key): pass
    def _onLinkValueChanged(self, host, key): pass


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ KVPath object
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVPath(object):
    _kvpath_ = None
    _inplace_ = True

    def __init__(self, kvpath=None, inplace=True):
        if isinstance(kvpath, basestring):
            kvpath = [p for p in kvpath.split('.') if p]
        else: kvpath = list(kvpath or [])

        selfVars = self.__dict__
        selfVars['_kvpath_'] = kvpath

        if not inplace:
            selfVars['_inplace_'] = False

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
        raise AttributeError("KVPath attributes are read-only")
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

kv = KVPath(inplace=False)

