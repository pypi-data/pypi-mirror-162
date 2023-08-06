# This file is placed in the Public Domain.


"configuration tests"


import unittest


from op.evt import Event
from op.obj import Object, edit, update


class Config(Object):

    pass


class Test_Config(unittest.TestCase):

    def test_parsegets(self):
        e = Event()
        e.parse("fnd object mod==irc")
        self.assertEqual(e.gets.mod, "irc")

    def test_parsesets(self):
        e = Event()
        e.parse("cfg bla  mod=irc")
        self.assertEqual(e.sets.mod, "irc")

    def test_edit(self):
        e = Event()
        o = Object()
        update(o, {"mod": "irc,rss"})
        edit(e, o)
        self.assertEqual(e.mod, "irc,rss")
