import unittest
from datetime import datetime
from decimal import Decimal

from scrapy.http import Request
from scrapyd.sqlite import JsonSqlitePriorityQueue, JsonSqliteDict


class JsonSqliteDictTest(unittest.TestCase):

    dict_class = JsonSqliteDict
    test_dict = {'hello': 'world', 'int': 1, 'float': 1.5, 'null': None,
                 'list': ['a', 'word'], 'dict': {'some': 'dict'}}

    def test_basic_types(self):
        test = self.test_dict
        d = self.dict_class()
        d.update(test)
        self.failUnlessEqual(list(d.items()), list(test.items()))
        d.clear()
        self.failIf(d.items())

    def test_in(self):
        d = self.dict_class()
        self.assertFalse('test' in d)
        d['test'] = 123
        self.assertTrue('test' in d)

    def test_keyerror(self):
        d = self.dict_class()
        self.assertRaises(KeyError, d.__getitem__, 'test')

    def test_replace(self):
        d = self.dict_class()
        self.assertEqual(d.get('test'), None)
        d['test'] = 123
        self.assertEqual(d.get('test'), 123)
        d['test'] = 456
        self.assertEqual(d.get('test'), 456)


class JsonSqlitePriorityQueueTest(unittest.TestCase):

    queue_class = JsonSqlitePriorityQueue

    supported_values = [
        "native ascii str",
        u"\xa3",
        123,
        1.2,
        True,
        ["a", "list", 1],
        {"a": "dict"},
    ]
    msg1 = "message 1"
    msg2 = "message 2"
    msg3 = "message 3"
    msg4 = "message 4"
    priority1 = 1.0
    priority2 = 5.0
    priority3 = 3.0
    priority4 = 2.0
    default_priority = 0.0

    def setUp(self):
        self.q = self.queue_class()

    def test_empty(self):
        self.failUnless(self.q.pop() is None)

    def test_one(self):
        msg = "a message"
        self.q.put(msg)
        self.failIf("_id" in msg)
        self.failUnlessEqual(self.q.pop(), (msg, self.default_priority))
        self.failUnless(self.q.pop() is None)

    def test_multiple(self):
        msg1 = "first message"
        msg2 = "second message"
        self.q.put(msg1)
        self.q.put(msg2)
        out = []
        out.append(self.q.pop())
        out.append(self.q.pop())
        self.failUnless((msg1, self.default_priority) in out)
        self.failUnless((msg2, self.default_priority) in out)
        self.failUnless(self.q.pop() is None)

    def test_priority(self):
        self.q.put(self.msg1, priority=self.priority1)
        self.q.put(self.msg2, priority=self.priority2)
        self.q.put(self.msg3, priority=self.priority3)
        self.q.put(self.msg4, priority=self.priority4)
        self.failUnlessEqual(self.q.pop(), (self.msg2, self.priority2))
        self.failUnlessEqual(self.q.pop(), (self.msg3, self.priority3))
        self.failUnlessEqual(self.q.pop(), (self.msg4, self.priority4))
        self.failUnlessEqual(self.q.pop(), (self.msg1, self.priority1))

    def test_iter_len_clear(self):
        self.failUnlessEqual(len(self.q), 0)
        self.failUnlessEqual(list(self.q), [])
        self.q.put(self.msg1, priority=self.priority1)
        self.q.put(self.msg2, priority=self.priority2)
        self.q.put(self.msg3, priority=self.priority3)
        self.q.put(self.msg4, priority=self.priority4)
        self.failUnlessEqual(len(self.q), 4)
        self.failUnlessEqual(list(self.q), \
            [(self.msg2, self.priority2), (self.msg3, self.priority3), (self.msg4, self.priority4), (self.msg1, self.priority1)])
        self.q.clear()
        self.failUnlessEqual(len(self.q), 0)
        self.failUnlessEqual(list(self.q), [])

    def test_remove(self):
        self.failUnlessEqual(len(self.q), 0)
        self.failUnlessEqual(list(self.q), [])
        msg1 = "good message 1"
        msg2 = "bad message 2"
        msg3 = "good message 3"
        msg4 = "bad message 4"
        self.q.put(msg1)
        self.q.put(msg2)
        self.q.put(msg3)
        self.q.put(msg4)
        self.q.remove(lambda x: x.startswith("bad"))
        self.failUnlessEqual(list(self.q), [(msg1, self.default_priority), (msg3, self.default_priority)])

    def test_types(self):
        for x in self.supported_values:
            self.q.put(x)
            self.failUnlessEqual(self.q.pop(), (x, self.default_priority))
