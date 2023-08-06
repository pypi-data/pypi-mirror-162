# This file is placed in the Public Domain.


"todo"


import time


from op.dbs import find, fntime
from op.obj import Object, save
from op.utl import elapsed


class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


def dne(event):
    if not event.args:
        return
    selector = {"txt": event.args[0]}
    for _fn, o in find("todo", selector):
        o._deleted = True
        save(o)
        event.reply("ok")
        break


def tdo(event):
    if not event.rest:
        nr = 0
        for _fn, o in find("todo"):
            event.reply("%s %s %s" % (nr, o.txt, elapsed(time.time() - fntime(_fn))))
            nr += 1
        return
    o = Todo()
    o.txt = event.rest
    save(o)
    event.reply("ok")
