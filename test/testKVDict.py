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

from TG.kvObserving import KVDict

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVDict(unittest.TestCase):
    def testDictOps(self):
        rhints = [0]

        kvd = KVDict()

        @kvd.kvpub.on('*')
        def onChange(kvlist, key):
            assert kvlist is kvd, (kvlist, kvd)
            assert key == '*', (key, "*")
            rhints[0] += 1

        self.assertEqual(rhints, [0])

        kvd["A"] = 42
        self.assertEqual(rhints, [1])

        del kvd["A"]
        self.assertEqual(rhints, [2])
    
        kvd.update((chr(65+i), i) for i in xrange(26))
        self.assertEqual(rhints, [3])

        # no change to hints because 'A' should already be in the dict
        kvd.setdefault('A', 1942)
        self.assertEqual(rhints, [3])

        kvd.setdefault('abba', 1942)
        self.assertEqual(rhints, [4])

        # no change to hints because 'notAKey' is not in the dict
        kvd.pop('notAKey', None)
        self.assertEqual(rhints, [4])

        kvd.pop('abba', None)
        self.assertEqual(rhints, [5])

        kvd.popitem()
        self.assertEqual(rhints, [6])

        kvd.clear()
        self.assertEqual(rhints, [7])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

