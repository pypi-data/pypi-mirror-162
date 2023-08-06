# This file is placed in the Public Domain.


"console"


import inspect
import time


from op.bus import Bus
from op.dbs import Class
from op.evt import Event, Command
from op.hdl import Callbacks, Handler
from op.obj import Default, Object, get, register


starttime = time.time()


class Table():

    mod = {}

    @staticmethod
    def add(o):
        Table.mod[o.__name__] = o

    @staticmethod
    def exec(cmd):
        for mod in Table.mod.values():
            f = getattr(mod, cmd, None)
            if f:
                f()

    @staticmethod
    def get(nm):
        return Table.mod.get(nm, None)

    @staticmethod
    def scan(mns=None):
        for mod in Table.mod.values():
            if mns and mod.__name__ not in mns:
                continue
            for _k, o in inspect.getmembers(mod, inspect.isfunction):
                if "event" in o.__code__.co_varnames:
                    Commands.add(o)
            for _k, clz in inspect.getmembers(mod, inspect.isclass):
                Class.add(clz)


class CLI(Handler):

    def __init__(self):
        Handler.__init__(self)
        Bus.add(self)

    def announce(self, txt):
        self.raw(txt)

    def cmd(self, txt):
        c = Command()
        c.channel = ""
        c.orig = repr(self)
        c.txt = txt
        self.handle(c)
        c.wait()

    def raw(self, txt):
        pass



class Commands(Object):

    cmd = Object()

    @staticmethod
    def add(cmd):
        register(Commands.cmd, cmd.__name__, cmd)

    @staticmethod
    def get(cmd):
        return get(Commands.cmd, cmd)


    @staticmethod
    def remove(cmd):
        del Commands.cmd[cmd]


Config = Default()


class Console(CLI):

    def handle(self, e):
        Handler.handle(self, e)
        e.wait()

    def poll(self):
        e = Command()
        e.channel = ""
        e.cmd = ""
        e.txt = input("> ")
        e.orig = repr(self)
        if e.txt:
            e.cmd = e.txt.split()[0]
        return e


def dispatch(e):
    e.parse()
    f = Commands.get(e.cmd)
    if f:
        f(e)
        e.show()
    e.ready()


def parse_cli(txt):
    e = Event()
    e.parse(txt)
    return e


Callbacks.add("command", dispatch)
