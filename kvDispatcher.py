##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2009  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

"""KVDispatcher's role is to collect as set of event updates.

One of the primary bennefits of the dispatcher is to catch exceptions and
reformat them to remove surpurfulous call stack entries for the KVPublish
machinery.
"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sys
import traceback

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def format_exception_stack(excInfo=None, limit=None, depth=1, splice=0):
    if excInfo is None:
        excInfo = sys.exc_info()

    fexc = traceback.format_exception(*excInfo)

    depth += 1
    if limit is not None:
        limit += depth
    stk = traceback.extract_stack(None, limit)[:-depth]
    fexc[1:1+splice] = traceback.format_list(stk)
    return fexc

def print_exception_stack(excInfo=None, limit=None, depth=1, splice=0, file=None):
    fexc = format_exception_stack(excInfo, limit, depth+1, splice)
    print >> file, ''.join(fexc)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVDispatcher(object):
    def __init__(self, host=None):
        if host is not None:
            host = host()
        self.host = host
        self._order = []

    def add(self, event, evtKey):
        evtList = list(event.inCallOrder())
        if evtList:
            self._order.append((evtKey, evtList))

    def __len__(self):
        return sum(len(e[-1]) for e in self._order)
    def inCallOrder(self):
        for evtKey, evtList in self._order:
            for evtFn in evtList:
                yield evtFn, evtKey
    __iter__ = inCallOrder

    def call(self):
        host = self.host
        for evtKey, evtList in self._order:
            for evtFn in evtList:
                try: 
                    evtFn(host, evtKey)
                except Exception:
                    if self.onException(evtFn, host, evtKey):
                        continue
                    else: raise
    __call__ = call

    def callEx(self, *args, **kw):
        host = self.host
        for evtKey, evtList in self._order:
            for evtFn in evtList:
                try: 
                    evtFn(host, evtKey, *args, **kw)
                except Exception:
                    if self.onException(evtFn, host, evtKey):
                        continue
                    else: raise

    stackLimit = 1
    def onException(self, evtFn, host, evtKey):
        print_exception_stack(None, self.stackLimit, depth=3, splice=1)
        return True
        
