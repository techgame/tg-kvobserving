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

from __future__ import with_statement

import unittest

from TG.kvObserving import KVObject, KVProperty, KVList, KVDict, KVWatcher, kvwatch, kv

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class KVDemoDepData(KVObject):
    kvpub = KVObject.kvpub.copy()

    left = KVProperty()
    right = KVProperty()

    def __init__(self, left=0, right=0):
        self.left = left
        self.right = right

    kvpub.depend('sum', ['left', 'right'])
    def getSum(self):
        return self.left + self.right
    sum = property(getSum)

    kvpub.depend('prod', ['left', 'right'])
    def getProd(self):
        return self.left * self.right
    prod = property(getProd)

    kvpub.depend('prodSum', ['prod', 'sum'])
    def getProdSum(self):
        return (self.prod, max(1, self.sum))
    prodSum = property(getProdSum)

    @kvpub.on('sum')
    def onMethodNotify(self, key):
        self.kvpub('methodNotify')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVDependentData(unittest.TestCase):
    def testSum(self):
        result = []
        demo = KVDemoDepData()

        @kvwatch(demo, kv.sum)
        def onSumChange(kvw, value):
            #print 'sum:', key, value
            result.append(value)

        self.assertEqual(result, [])

        demo.left = 2
        self.assertEqual(result[-1], 2)

        demo.right = 9
        self.assertEqual(result[-1], 11)
    
    def testProd(self):
        result = []
        demo = KVDemoDepData()

        @kvwatch(demo, kv.prod)
        def onProdChange(kvw, value):
            #print 'prod:', key, value
            result.append(value)

        self.assertEqual(result, [])

        demo.left = 2
        self.assertEqual(result[-1], 0)

        demo.right = 9
        self.assertEqual(result[-1], 18)

        demo.left = 7
        self.assertEqual(result[-1], 63)
    
    def testProdSum(self):
        result = []
        demo = KVDemoDepData()

        @kvwatch(demo, kv.prodSum)
        def onProdSumChange(kvw, value):
            result.append(value)

        self.assertEqual(result, [])

        demo.left = 2
        self.assertEqual(result[-1], (0, 2))

        demo.right = 9
        self.assertEqual(result[-1], (18, 11))

        demo.left = 7
        self.assertEqual(result[-1], (63, 16))
    
    def testMethodNotify(self):
        result = [0]
        demo = KVDemoDepData()

        @kvwatch(demo, kv.methodNotify)
        def onMethodNotify(kvw, value):
            result[0] += 1

        self.assertEqual(result, [0])

        demo.left = 2
        self.assertEqual(result, [1])

        demo.right = 9
        self.assertEqual(result, [2])

        demo.left = 7
        self.assertEqual(result, [3])

        with demo.kvpub:
            demo.right = 3
            demo.left = 5
            self.assertEqual(result, [3])
        self.assertEqual(result, [5])

    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

