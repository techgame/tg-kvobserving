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

from TG.kvObserving import KVList

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVList(unittest.TestCase):
    def testListOps(self):
        rhints = [0]

        kvl = KVList()

        @kvl.kvpub.on('*')
        def onChange(kvlist, key):
            assert kvlist is kvl, (kvlist, kvl)
            assert key == '*', (key, "*")
            rhints[0] += 1

        self.assertEqual(rhints, [0])

        kvl.append("A")
        self.assertEqual(rhints, [1])
    
        kvl[0] = 'B'
        self.assertEqual(rhints, [2])
    
        del kvl[0]
        self.assertEqual(rhints, [3])
    
        kvl.extend(range(10))
        self.assertEqual(rhints, [4])

        kvl[3:7] = ['A', 'B', 'C', 'D']
        self.assertEqual(rhints, [5])

        del kvl[3:7]
        self.assertEqual(rhints, [6])

        kvl += ['ugg', 'abug']
        self.assertEqual(rhints, [7])

        kvl.insert(2, 'squish')
        self.assertEqual(rhints, [8])

        kvl.remove('ugg')
        self.assertEqual(rhints, [9])
    
        kvl.pop(-2)
        self.assertEqual(rhints, [10])
    
        kvl.sort()
        self.assertEqual(rhints, [11])
    
        kvl.reverse()
        self.assertEqual(rhints, [12])
    
        kvl[::] = [2, 3, 4]
        self.assertEqual(rhints, [13])
    
        kvl *= 3
        self.assertEqual(rhints, [14])
    
        del kvl[:]
        self.assertEqual(rhints, [15])
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

