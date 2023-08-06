import sys
import functools
import delune
import types
from pprint import pprint
from rs4 import argopt


def _create ():
    return dl.create (colname, data_dirs or [colname], version, **opts)

def _drop (name):
    assert name == colname
    dl.drop (colname, True)

def _qdelete (q):
    with col:
        col.qdelete (q)
        col.commit ()

def _ddelete (docid):
    with col:
        col.delete (docid)
        col.commit ()

def _search (q, offset = 0, limit = 3):
    with col:
        pprint (col.search (q, int (offset), int (limit)))

def _truncate (name):
    assert name == colname
    with col:
       col.truncate (name)

def _index ():
    raise NotImplementedError

def _delete ():
    raise NotImplementedError

#------------------------------------------------
FUNCS = dict (
    before_search = lambda: None,
    search = _search,
    searched = lambda: None,

    before_create = lambda: None,
    create = _create,
    created = lambda: None,

    before_index = lambda: None,
    index = _index,
    indexed = lambda: None,

    before_delete = lambda: None,
    delete = _delete,
    qdelete = _qdelete,
    ddelete = _ddelete,
    deleted = lambda: None,

    before_truncate = lambda: None,
    truncate = _truncate,
    truncated = lambda: None,

    before_drop = lambda: None,
    drop = _drop,
    dropped = lambda: None,
)

NO_OVERIDES = {'search', 'create', 'qdelete', 'ddelete', 'truncate', 'drop'}

def mapname (name):
    def map (f):
        FUNCS [name] = f
    return map

for k, v in FUNCS.items ():
    if k in NO_OVERIDES:
        continue
    setattr (sys.modules [__name__], k, mapname (k))

def sequencial (a, b, c, *args, **kargs):
    FUNCS [a] ()
    r = FUNCS [b] (*args, **kargs)
    FUNCS [c] ()
    return r


#------------------------------------------------
dl, col, colname = None, None, None
opts, data_dirs, version = {}, None, 1

def setup (endpoint, conf = {}):
    global dl, col, opts, data_dirs, version, colname

    server, colname = endpoint.split ('/cols/')
    dl = delune.mount (server)

    if 'data_dirs' in conf:
        data_dirs = conf.pop ('data_dirs')
    if 'version' in conf:
        version = conf.pop ('version')
    opts = conf

    try:
        col = dl.load (colname)
    except NameError:
        pass
    return col

def handle_argv (endpoint, conf = {}):
    argv = argopt.options ().argv
    setup (endpoint, conf)
    cmd = len (argv) >= 1 and argv [0] or '-'

    if not col and cmd not in ('create', 'help'):
        raise NameError ('collection not created')

    if cmd == "index":
        return sequencial ('before_index', 'index', 'indexed')

    elif cmd == "delete":
        return sequencial ('before_delete', cmd, 'deleted')

    # only command line ------------------------------
    elif cmd == "config":
        for k, v in opts.items ():
            col.setopt (k, **v)
        pprint (col.config)

    elif cmd == "inspect":
        pprint (col.status ())

    elif cmd == "create":
        return sequencial ('before_create', 'create', 'created')

    elif cmd == "truncate":
        assert len (argv) >= 2, "collection name required"
        return sequencial ('before_truncate', 'truncate', 'truncated', argv [1])

    elif cmd.endswith ("delete"): # qdelete, ddelete
        assert len (argv) >= 2, "q or docId required"
        return sequencial ('before_delete', cmd, 'deleted', argv [1])

    elif cmd == "search":
        assert len (argv) >= 2, "q required"
        return sequencial ('before_search', 'search', 'searched', *argv [1:])

    elif cmd == "drop":
        assert len (argv) >= 2, "collection name required"
        return sequencial ('before_drop', 'drop', 'dropped', argv [1])

    elif cmd == "help":
        print ("Usage:")
        print ("  script.py COMMAND [OPTION, ...]")
        print ("Commands:")
        print ("  create, config, index, delete, qdelete, ddelete, inspect, truncate, drop, search, help")

    return cmd
