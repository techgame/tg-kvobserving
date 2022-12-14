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

import unittest
from TG.kvObserving import KVObject, KVProperty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVObserve(unittest.TestCase):
    def testSimple(self):
        result = []
        class DemoObj(KVObject):
            kvobserve = KVObject.kvobserve
            left = KVProperty(None).fetchOnInit()

            @kvobserve('left')
            def change(self, value):
                result.append(value)

        d = DemoObj()

        self.assertEqual(result, [None])

        d.left = 2

        self.assertEqual(result, [None, 2])
    
    def testPathWithNonKVObject(self):
        class fobject(object): pass

        result = []
        class DemoObj(KVObject):
            kvobserve = KVObject.kvobserve
            left = KVProperty(None).fetchOnInit()

            @kvobserve('left.fun')
            def change(self, value):
                result.append(value)

        d = DemoObj()
        self.assertEqual(result, [None])

        d.left = 2
        self.assertEqual(result, [None, None])

        f = fobject()
        f.fun = 42
        d.left = f

        self.assertEqual(result, [None, None, 42])

        f.fun = 'no update'
        self.assertEqual(result, [None, None, 42])

        f.fun = 'manual update'
        d.left = f
        self.assertEqual(result, [None, None, 42, 'manual update'])
    
    def testPath(self):
        class tobject(KVObject): 
            fun = KVProperty(None).fetchOnInit()

        result = []
        class DemoObj(KVObject):
            kvobserve = KVObject.kvobserve
            left = KVProperty(None).fetchOnInit()

            @kvobserve('left.fun')
            def change(self, value):
                result.append(value)

        d = DemoObj()
        self.assertEqual(result, [None])

        d.left = 2
        self.assertEqual(result, [None, None])

        t = tobject()
        t.fun = 42
        d.left = t

        self.assertEqual(result, [None, None, 42])

        t.fun = 'update'
        self.assertEqual(result, [None, None, 42, 'update'])
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

