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

from TG.kvObserving import KVSet

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVDict(unittest.TestCase):
    def testDictOps(self):
        rhints = [0]

        kvd = KVSet()

        @kvd.kvpub.on('*')
        def onChange(kvlist, key):
            assert kvlist is kvd, (kvlist, kvd)
            assert key == '*', (key, "*")
            rhints[0] += 1

        self.assertEqual(rhints, [0])

        kvd.add("A")
        self.assertEqual(rhints, [1])

        kvd.remove("A")
        self.assertEqual(rhints, [2])
    
        kvd.update(chr(65+i) for i in xrange(26))
        self.assertEqual(rhints, [3])

        kvd.remove("B")
        self.assertEqual(rhints, [4])

        kvd.discard("C")
        self.assertEqual(rhints, [5])

        kvd.pop()
        self.assertEqual(rhints, [6])

        kvd -= set(("F", "G", "H"))
        self.assertEqual(rhints, [7])

        kvd.difference_update('IJK')
        self.assertEqual(rhints, [8])

        kvd |= set('HI')
        self.assertEqual(rhints, [9])

        kvd.update('GHIJ')
        self.assertEqual(rhints, [10])

        kvd ^= set('ABCDEFGHIJK')
        self.assertEqual(rhints, [11])

        kvd.symmetric_difference_update('IJKLMN')
        self.assertEqual(rhints, [12])

        kvd.clear()
        self.assertEqual(rhints, [13])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

