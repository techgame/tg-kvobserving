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
            left = KVProperty(None)

            @kvobserve('left')
            def change(self, value):
                result.append(value)

        d = DemoObj()

        self.assertEqual(result, [None])

        d.left = 2

        self.assertEqual(result, [None, 2])
    
    def testPath(self):
        class fobject(object): pass

        result = []
        class DemoObj(KVObject):
            kvobserve = KVObject.kvobserve
            left = KVProperty(None)

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
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

