# This file is placed in the Public Domain.


"object database"


import op
import os
import time
import _thread


from op.obj import Object, search, update
from op.obj import load, save
from op.utl import locked


dblock = _thread.allocate_lock()


class ENOPATH(Exception):

    pass

class Class():

    cls = {}

    @staticmethod
    def add(clz):
        Class.cls["%s.%s" % (clz.__module__, clz.__name__)] =  clz

    @staticmethod
    def full(name):
        name = name.lower()
        res = []
        for cln in Class.cls:
            if cln.split(".")[-1].lower() == name:
                res.append(cln)
        return res

    @staticmethod
    def get(nm):
        return Class.cls.get(nm, None)

    @staticmethod
    def remove(mn):
        del Class.cls[mn]


class Db(Object):

    names = Object()

    def all(self, otype, timed=None):
        nr = -1
        result = []
        for fn in fns(otype, timed):
            o = hook(fn)
            if "_deleted" in o and o._deleted:
                continue
            nr += 1
            result.append((fn, o))
        if not result:
            return []
        return result

    def find(self, otype, selector=None, index=None, timed=None):
        if selector is None:
            selector = {}
        nr = -1
        result = []
        for fn in fns(otype, timed):
            o = hook(fn)
            if selector and not search(o, selector):
                continue
            if "_deleted" in o and o._deleted:
                continue
            nr += 1
            if index is not None and nr != index:
                continue
            result.append((fn, o))
        if not result:
            return []
        return result

    def lastmatch(self, otype, selector=None, index=None, timed=None):
        db = Db()
        res = sorted(db.find(otype, selector, index, timed),
                     key=lambda x: fntime(x[0]))
        if res:
            return res[-1]
        return (None, None)

    def lasttype(self, otype):
        fnn = fns(otype)
        if fnn:
            return hook(fnn[-1])
        return None

    def lastfn(self, otype):
        fn = fns(otype)
        if fn:
            fnn = fn[-1]
            return (fnn, hook(fnn))
        return (None, None)

    def remove(self, otype, selector=None):
        has = []
        for _fn, o in self.find(otype, selector or {}):
            o._deleted = True
            has.append(o)
        for o in has:
            save(o)
        return has

    @staticmethod
    def types():
        assert op.obj.workdir
        path = os.path.join(op.obj.workdir, "store")
        if not os.path.exists(path):
            return []
        return sorted(os.listdir(path))


def fntime(daystr):
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.split(".")[0]
    return time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))


@locked(dblock)
def fns(name, timed=None):
    if not name:
        return []
    assert op.obj.workdir
    p = os.path.join(op.obj.workdir, "store", name) + os.sep
    if not os.path.exists(p):
        return []
    res = []
    d = ""
    for rootdir, dirs, _files in os.walk(p, topdown=False):
        if dirs:
            d = sorted(dirs)[-1]
            if d.count("-") == 2:
                dd = os.path.join(rootdir, d)
                fls = sorted(os.listdir(dd))
                if fls:
                    p = os.path.join(dd, fls[-1])
                    if (
                        timed
                        and "from" in timed
                        and timed["from"]
                        and fntime(p) < timed["from"]
                    ):
                        continue
                    if timed and timed.to and fntime(p) > timed.to:
                        continue
                    res.append(p)
    return sorted(res, key=fntime)


@locked(dblock)
def hook(hfn):
    if hfn.count(os.sep) > 3:
        oname = hfn.split(os.sep)[-4:]
    else:
        oname = hfn.split(os.sep)
    cname = oname[0]
    cls = Class.get(cname)
    if cls:
        o = cls()
    else:
        o = Object()
    fn = os.sep.join(oname)
    load(o, fn)
    return o


def listfiles(workdir):
    path = os.path.join(workdir, "store")
    if not os.path.exists(path):
        return []
    return sorted(os.listdir(path))


def all(timed=None):
    assert op.obj.workdir
    p = os.path.join(op.obj.workdir, "store")
    for name in os.listdir(p):
        for fn in fns(name):
            yield fn


def find(name, selector=None, index=None, timed=None, names=None):
    db = Db()
    if not names:
        names = Class.full(name)
    for n in names:
        for fn, o in db.find(n, selector, index, timed):
            yield fn, o


def last(o):
    db = Db()
    path, obj = db.lastfn(o.__otype__)
    if obj:
        update(o, obj)
    if path:
        splitted = path.split(os.sep)
        stp = os.sep.join(splitted[-4:])
        return stp
    return None
