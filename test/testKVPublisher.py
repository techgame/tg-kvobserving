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

from TG.kvObserving.kvObject import KVObjectType
from TG.kvObserving.kvPublisher import KVPublisher

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVPublisher(unittest.TestCase):
    def testCreation(self):
        class AnObservable(object):
            __metaclass__ = KVObjectType
            kvpub = KVPublisher()
        t = AnObservable()

    def testObservations(self):
        result = []

        class AnObservable(object):
            __metaclass__ = KVObjectType
            kvpub = KVPublisher()

            @kvpub.on('a')
            def testA(self, key):
                assert isinstance(self, AnObservable)
                result.append('testA:'+key)

        @AnObservable.kvpub.on('b')
        def testB(self, key):
            result.append('testB:'+key)
        
        t = AnObservable()

        @t.kvpub.on('c')
        def testC(self, key):
            result.append('testC:'+key)

        self.assertEqual(result, [])

        t.kvpub('a')
        self.assertEqual(result, ['testA:a'])

        t.kvpub('b')
        self.assertEqual(result, ['testA:a', 'testB:b'])

        t.kvpub('c')
        self.assertEqual(result, ['testA:a', 'testB:b', 'testC:c'])


    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

