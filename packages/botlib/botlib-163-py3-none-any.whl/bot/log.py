# This file is placed in the Public Domain.


"log"


from op.obj import Object, save


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


def log(event):
    if not event.rest:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.rest
    save(o)
    event.reply("ok")
