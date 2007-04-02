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

class KVNode(KVObject):
    data = KVProperty()
    left = KVProperty()
    right = KVProperty()

    def __init__(self, data=None, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

    def __repr__(self):
        return '<KVNode %r>' % (self.data,)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVObserver(unittest.TestCase):
    def setUp(self):
        self.tree = KVNode('a',
                KVNode('b',
                    KVNode('c'),
                    KVNode('d')),
                KVNode('e',
                    KVNode('f'),
                    KVNode('g'))
                )

    def testOneLevel(self):
        result = []
        tree = self.tree

        @kvwatch(tree, kv.data)
        def evt(kvw, value):
            result.append(value)

        self.assertEqual(result, [])

        tree.data = 'alpha'
        self.assertEqual(result, ['alpha'])

        tree.data = 'alphabet'
        self.assertEqual(result, ['alpha', 'alphabet'])

    def testContextWithMultipleChange(self):
        result = []
        tree = self.tree

        @kvwatch(tree, kv.data)
        def evt(kvw, value):
            result.append(value)

        self.assertEqual(result, [])

        with tree.kvpub:
            tree.data = 'alpha'
            self.assertEqual(result, [])

            tree.data = 'alphabet'
            self.assertEqual(result, [])

        self.assertEqual(result, ['alphabet'])

    def testTwoLevel(self):
        result = []
        tree = self.tree

        @kvwatch(tree, kv.left.data)
        def evt(kvw, value):
            result.append(value)

        self.assertEqual(result, [])

        tree.left.data = 'beta'
        self.assertEqual(result, ['beta'])

        tree.left = tree.right.left
        self.assertEqual(result, ['beta', 'f'])

    def testThreeLevel(self):
        result = []
        tree = self.tree

        @kvwatch(tree, kv.left.right.data)
        def evt(kvw, value):
            result.append(value)

        self.assertEqual(result, [])

        tree.left.right.data = 'delta'
        self.assertEqual(result, ['delta'])

        tree.left.right = tree.right.left
        self.assertEqual(result, ['delta', 'f'])

        tree.left = tree.right
        self.assertEqual(result, ['delta', 'f', 'g'])

    def testTwoLevelString(self):
        result = []
        tree = self.tree

        @kvwatch(tree, 'left.data')
        def evt(kvw, value):
            result.append(value)

        self.assertEqual(result, [])

        tree.left.data = 'beta'
        self.assertEqual(result, ['beta'])

        tree.left = tree.right.left
        self.assertEqual(result, ['beta', 'f'])

    def testThreeLevelString(self):
        result = []
        tree = self.tree

        @kvwatch(tree, 'left.right.data')
        def evt(kvw, value):
            result.append(value)

        self.assertEqual(result, [])

        tree.left.right.data = 'delta'
        self.assertEqual(result, ['delta'])

        tree.left.right = tree.right.left
        self.assertEqual(result, ['delta', 'f'])

        tree.left = tree.right
        self.assertEqual(result, ['delta', 'f', 'g'])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestKVWatcher(unittest.TestCase):
    def setUp(self):
        self.tree = KVNode('a',
                        KVNode(KVList(['c', 'd', 'f', 'g'])),
                        KVNode(KVDict({'h': 2, 'i': 3, 'j': 4, 'k': 5})))

    def testListChange(self):
        result = []
        tree = self.tree

        @kvwatch(tree, kv.left.data[...])
        def evt(kvw, value):
            result.append(value.copy())

        self.assertEqual(result, [])

        tree.left.data.sort(reverse=True)

        self.assertEqual(result, [['g', 'f', 'd', 'c']])

        del tree.left.data[2:]
        self.assertEqual(result[-1], ['g', 'f'])

        tree.left.data[:] = list('kvwatchers')

        self.assertEqual(result[-1], list('kvwatchers'))

    def testDictChange(self):
        result = []
        tree = self.tree

        @kvwatch(tree, kv.right.data[...])
        def evt(kvw, value):
            result.append(value.copy())

        self.assertEqual(result, [])

        self.assertEqual(tree.right.data.pop('j'), 4)

        self.assertEqual(result[-1], {'h': 2, 'i': 3, 'k': 5})

        self.assertEqual(tree.right.data.setdefault('i', 23), 3)
        self.assertEqual(result[-1], {'h': 2, 'i': 3, 'k': 5})

        self.assertEqual(tree.right.data.setdefault('l', 23), 23)
        self.assertEqual(result[-1], {'h': 2, 'i': 3, 'k': 5, 'l':23})

        del tree.right.data['i']
        self.assertEqual(result[-1], {'h': 2, 'k': 5, 'l':23})

        del tree.right.data['h']
        self.assertEqual(result[-1], {'k': 5, 'l':23})

        tree.right.data['l'] = 42
        self.assertEqual(result[-1], {'k': 5, 'l':42})


class TestKVWatcherDependency(unittest.TestCase):
    def testSelectDependency(self):
        tree = KVNode(
                        KVList([
                            KVNode('alpha'),
                            KVNode('beta'),
                            KVNode('gamma')]),
                        )

        result = []
        watchData = KVWatcher(tree, kv.data[...])

        @watchData.add
        def onDataChange(kvw, value):
            kvw.select = value[0]

        @kvwatch(watchData, kv.select.data)
        def onSelectChange(kvw, value):
            result.append(value)

        self.assertEqual(result, [])

        watchData.relink()
        self.assertEqual(result, ['alpha'])

        tree.data.reverse()
        self.assertEqual(result, ['alpha', 'gamma'])
        
        with tree.data.kvpub:
            gamma = tree.data.pop(0)
            tree.data.append(gamma)
            self.assertEqual(result, ['alpha', 'gamma'])

        self.assertEqual(result, ['alpha', 'gamma', 'beta'])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

