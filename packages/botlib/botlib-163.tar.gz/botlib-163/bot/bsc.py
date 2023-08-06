# This file is placed in the Public Domain.


"basic"


import time


from op.run import Commands, starttime
from op.utl import elapsed


def cmd(event):
    event.reply(",".join(sorted(Commands.cmd)))


def upt(event):
    event.reply(elapsed(time.time()-starttime))


def ver(event):
    event.reply("BOTLIB 163")
