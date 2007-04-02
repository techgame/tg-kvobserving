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

import unittest

from TG.kvObserving import KVObject, KVProperty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVPublisher(unittest.TestCase):
    def testCreation(self):
        class AnObservable(KVObject):
            pass
        t = AnObservable()

    def testObservations(self):
        result = []

        class AnObservable(KVObject):
            kvpub = KVObject.kvpub.copy()

            @kvpub.on('a')
            def testA(self, key, hint=None):
                assert isinstance(self, AnObservable)
                result.append('testA:'+key)

        @AnObservable.kvpub.on('b')
        def testB(self, key, hint=None):
            result.append('testB:'+key)
        
        t = AnObservable()

        @t.kvpub.on('c')
        def testC(self, key, hint=None):
            result.append('testC:'+key)

        self.assertEqual(result, [])

        t.kvpub('a')
        self.assertEqual(result, ['testA:a'])

        t.kvpub('b')
        self.assertEqual(result, ['testA:a', 'testB:b'])

        t.kvpub('c')
        self.assertEqual(result, ['testA:a', 'testB:b', 'testC:c'])

    def testKVProperty(self):
        result = []

        class AnObservable(KVObject):
            kvpub = KVObject.kvpub.copy()

            a = KVProperty()
            b = KVProperty()
            c = KVProperty()

            @kvpub.on('a')
            def testA(self, key, hint=None):
                assert isinstance(self, AnObservable)
                result.append('testA:'+key)

        @AnObservable.kvpub.on('b')
        def testB(self, key, hint=None):
            result.append('testB:'+key)
        
        t = AnObservable()

        @t.kvpub.on('c')
        def testC(self, key, hint=None):
            result.append('testC:'+key)

        self.assertEqual(result, [])

        t.a = 'issue update for "a"'
        self.assertEqual(result, ['testA:a'])

        t.b = 'issue update for "b"'
        self.assertEqual(result, ['testA:a', 'testB:b'])

        t.c = 'issue update for "c"'
        self.assertEqual(result, ['testA:a', 'testB:b', 'testC:c'])



    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

